"""Booking workflow: seat holds, passenger capture, confirmation, expiry."""
from datetime import datetime, timedelta

from flask import current_app
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Booking, BookingSeat, Passenger, Seat
from app.repositories.booking_repository import BookingRepository
from app.repositories.flight_repository import FlightRepository
from app.utils.helpers import utcnow
from app.utils.validators import validate_booking_contact, validate_passenger


class BookingError(Exception):
    """Raised when a booking operation cannot proceed."""


class BookingService:
    MAX_SEATS = 6

    def __init__(self, repo: BookingRepository | None = None,
                 flight_repo: FlightRepository | None = None):
        self.repo = repo or BookingRepository()
        self.flight_repo = flight_repo or FlightRepository()

    # ------------------------------------------------------------------
    # Hold expiry sweeper
    # ------------------------------------------------------------------
    def expire_stale_holds(self, commit: bool = True) -> int:
        """Release seats held by PENDING bookings whose hold has lapsed."""
        expired = self.repo.expired_pending_bookings()
        count = 0
        for booking in expired:
            self.repo.release_seats(booking)
            booking.booking_status = Booking.STATUS_EXPIRED
            booking.hold_expires_at = None
            if booking.payment and booking.payment.payment_status == "PENDING":
                booking.payment.payment_status = "FAILED"
                booking.payment.gateway_message = "Seat hold expired before payment."
            count += 1
        if count and commit:
            db.session.commit()
        return count

    # ------------------------------------------------------------------
    # Step 1-4: create pending booking and hold seats atomically
    # ------------------------------------------------------------------
    def create_pending_booking(
        self,
        user,
        schedule_id: int,
        seat_ids: list[int],
        contact_email: str | None = None,
        contact_phone: str | None = None,
    ) -> Booking:
        """Reserve the requested seats for a limited hold window.

        Uses a single transaction with ``SELECT ... FOR UPDATE`` on the seat rows
        so concurrent attempts on the same seat cannot both succeed.
        """
        self.expire_stale_holds()

        schedule = self.flight_repo.get_schedule(schedule_id)
        if not schedule:
            raise BookingError("That flight is no longer available.")
        if schedule.status != "SCHEDULED" or schedule.departure_time <= utcnow():
            raise BookingError("This flight has already departed or is not open for booking.")
        if schedule.flight.source_airport_id == schedule.flight.destination_airport_id:
            raise BookingError("Invalid route.")

        seat_ids = [int(s) for s in seat_ids]
        if not seat_ids:
            raise BookingError("Please select at least one seat.")
        if len(seat_ids) > self.MAX_SEATS:
            raise BookingError(f"You can book at most {self.MAX_SEATS} seats at once.")
        if len(set(seat_ids)) != len(seat_ids):
            raise BookingError("Duplicate seats were submitted.")

        contact_email = (contact_email or getattr(user, "email", "") or "").strip()
        contact_phone = (contact_phone or getattr(user, "phone", "") or "").strip()
        contact_errors = validate_booking_contact(contact_email, contact_phone)
        if contact_errors:
            raise BookingError(" ".join(contact_errors))

        hold_minutes = current_app.config.get("SEAT_HOLD_MINUTES", 10)
        booking = Booking(
            user_id=user.user_id,
            schedule_id=schedule.schedule_id,
            booking_status=Booking.STATUS_PENDING,
            contact_email=contact_email,
            contact_phone=contact_phone,
            total_amount=0,
            hold_expires_at=utcnow() + timedelta(minutes=hold_minutes),
        )
        db.session.add(booking)
        try:
            db.session.flush()

            # Row-level lock, then re-check every seat inside the transaction.
            locked = self.repo.lock_seats_for_update(schedule.schedule_id, seat_ids)
            if len(locked) != len(seat_ids):
                raise BookingError("One or more selected seats do not exist on this flight.")

            total = 0.0
            for seat in locked:
                if seat.status != Seat.STATUS_AVAILABLE:
                    raise BookingError(
                        f"Seat {seat.seat_number} was just taken. Please pick another seat."
                    )
                price = schedule.seat_price(seat.seat_class)
                seat.status = Seat.STATUS_HELD
                seat.current_booking_id = booking.booking_id
                db.session.add(
                    BookingSeat(
                        booking_id=booking.booking_id,
                        seat_id=seat.seat_id,
                        active_seat_id=seat.seat_id,
                        is_active=True,
                        price=price,
                    )
                )
                total += price

            booking.total_amount = round(total, 2)
            db.session.commit()
            return booking
        except BookingError:
            db.session.rollback()
            raise
        except IntegrityError:
            db.session.rollback()
            raise BookingError("Those seats were just reserved by another passenger.")
        except Exception as exc:
            current_app.logger.exception("Booking creation failed: %s", exc)
            db.session.rollback()
            raise

    # ------------------------------------------------------------------
    # Step 5: passenger information
    # ------------------------------------------------------------------
    def save_passengers(self, booking: Booking, passenger_payloads: list[dict]) -> list[str]:
        """Validate and store passenger rows. Returns a list of errors."""
        if booking.booking_status != Booking.STATUS_PENDING:
            return ["This booking can no longer be edited."]
        if booking.is_hold_expired:
            return ["Your seat hold has expired. Please start a new booking."]

        expected = len(booking.active_seats)
        if len(passenger_payloads) != expected:
            return [f"Provide details for exactly {expected} passenger(s)."]

        errors: list[str] = []
        cleaned: list[dict] = []
        for index, payload in enumerate(passenger_payloads, start=1):
            data, problems = validate_passenger(payload)
            if problems:
                errors.extend(f"Passenger {index}: {message}" for message in problems)
            cleaned.append(data)

        # Reject duplicate identification documents within one booking.
        seen_ids = [c.get("identification_number") for c in cleaned if c.get("identification_number")]
        if len(seen_ids) != len(set(seen_ids)):
            errors.append("Duplicate identification numbers in the same booking.")

        if errors:
            return errors

        # Replace any previously stored passengers.
        Passenger.query.filter_by(booking_id=booking.booking_id).delete()
        seats = sorted(booking.active_seats, key=lambda s: s.seat_number)
        for data, seat in zip(cleaned, seats):
            db.session.add(
                Passenger(
                    booking_id=booking.booking_id,
                    full_name=data["full_name"],
                    date_of_birth=data["date_of_birth"],
                    gender=data["gender"],
                    identification_type=data["identification_type"],
                    identification_number=data["identification_number"],
                    seat_id=seat.seat_id,
                )
            )
        try:
            db.session.commit()
        except Exception as exc:
            current_app.logger.exception("Saving passengers failed: %s", exc)
            db.session.rollback()
            raise
        return []

    # ------------------------------------------------------------------
    # Step 8: confirmation (called after successful payment)
    # ------------------------------------------------------------------
    def confirm_booking(self, booking: Booking) -> Booking:
        booking.booking_status = Booking.STATUS_CONFIRMED
        booking.hold_expires_at = None
        for link in booking.seat_links:
            if link.is_active and link.seat:
                link.seat.status = Seat.STATUS_BOOKED
                link.seat.current_booking_id = booking.booking_id
        db.session.add(booking)
        return booking

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def get_owned_booking(self, booking_id: int, user) -> Booking | None:
        booking = self.repo.get_by_id(booking_id)
        if booking and booking.user_id == user.user_id:
            return booking
        return None

    def get_booking_by_reference(self, reference: str) -> Booking | None:
        return self.repo.get_by_reference(reference)

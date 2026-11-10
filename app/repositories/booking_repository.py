"""Booking data access including transactional seat locking."""
from datetime import datetime, timedelta

from sqlalchemy import select

from app.extensions import db
from app.models import Booking, BookingSeat, Passenger, Seat
from app.utils.helpers import utcnow


class BookingRepository:
    @staticmethod
    def get_by_id(booking_id: int) -> Booking | None:
        return db.session.get(Booking, int(booking_id))

    @staticmethod
    def get_by_reference(reference: str) -> Booking | None:
        return Booking.query.filter_by(booking_reference=reference).first()

    @staticmethod
    def get_for_user(booking_id: int, user_id: int) -> Booking | None:
        booking = db.session.get(Booking, int(booking_id))
        if booking and booking.user_id == user_id:
            return booking
        return None

    @staticmethod
    def list_for_user(user_id: int):
        return (
            Booking.query.filter_by(user_id=user_id)
            .order_by(Booking.created_at.desc())
            .all()
        )

    # ---- locking ----------------------------------------------------------
    @staticmethod
    def lock_seats_for_update(schedule_id: int, seat_ids: list[int]):
        """Row-lock the requested seat rows.

        ``SELECT ... FOR UPDATE`` serialises concurrent booking attempts so two
        transactions can never both hold the same seat.
        """
        stmt = (
            select(Seat)
            .where(Seat.schedule_id == schedule_id, Seat.seat_id.in_(seat_ids))
            .with_for_update()
        )
        return db.session.execute(stmt).scalars().all()

    @staticmethod
    def get_active_seat_links(seat_ids: list[int]):
        if not seat_ids:
            return []
        return (
            BookingSeat.query.filter(
                BookingSeat.seat_id.in_(seat_ids), BookingSeat.is_active.is_(True)
            ).all()
        )

    # ---- hold expiry ------------------------------------------------------
    @staticmethod
    def expired_pending_bookings(now: datetime | None = None):
        now = now or utcnow()
        return (
            Booking.query.filter(
                Booking.booking_status == Booking.STATUS_PENDING,
                Booking.hold_expires_at.isnot(None),
                Booking.hold_expires_at < now,
            )
            .with_for_update()
            .all()
        )

    @staticmethod
    def stats() -> dict:
        from sqlalchemy import func

        from app.models import Payment

        total_bookings = db.session.query(func.count(Booking.booking_id)).scalar() or 0
        confirmed = (
            db.session.query(func.count(Booking.booking_id))
            .filter(Booking.booking_status == Booking.STATUS_CONFIRMED)
            .scalar()
            or 0
        )
        cancelled = (
            db.session.query(func.count(Booking.booking_id))
            .filter(Booking.booking_status == Booking.STATUS_CANCELLED)
            .scalar()
            or 0
        )
        revenue = (
            db.session.query(func.coalesce(func.sum(Payment.amount), 0))
            .filter(Payment.payment_status == Payment.STATUS_SUCCESS)
            .scalar()
            or 0
        )
        return {
            "total_bookings": total_bookings,
            "confirmed": confirmed,
            "cancelled": cancelled,
            "revenue": float(revenue),
        }

    @staticmethod
    def recent(limit: int = 10):
        return Booking.query.order_by(Booking.created_at.desc()).limit(limit).all()

    @staticmethod
    def release_seats(booking: Booking) -> int:
        """Release all seats held by a booking. Returns the number released."""
        released = 0
        for link in booking.seat_links:
            if not link.is_active:
                continue
            seat = link.seat or db.session.get(Seat, link.seat_id)
            if seat and seat.current_booking_id == booking.booking_id:
                seat.status = Seat.STATUS_AVAILABLE
                seat.current_booking_id = None
            link.release()
            released += 1
        return released

"""Cancellation, refund calculation and seat release."""
from datetime import datetime

from flask import current_app

from app.extensions import db
from app.models import Booking, Cancellation, Payment
from app.repositories.booking_repository import BookingRepository
from app.utils.helpers import utcnow


class CancellationError(Exception):
    pass


class CancellationService:
    def __init__(self, repo: BookingRepository | None = None):
        self.repo = repo or BookingRepository()

    # ------------------------------------------------------------------
    @staticmethod
    def refund_quote(booking: Booking) -> dict:
        """Compute the refund for a booking under the configured policy."""
        amount = float(booking.total_amount or 0)
        fee_percent = float(current_app.config.get("CANCELLATION_FEE_PERCENT", 10))
        fee = round(amount * fee_percent / 100, 2)
        refund = round(amount - fee, 2)
        return {
            "amount": amount,
            "fee_percent": fee_percent,
            "fee": fee,
            "refund": max(refund, 0.0),
        }

    @staticmethod
    def eligibility(booking: Booking) -> tuple[bool, str]:
        if booking.booking_status == Booking.STATUS_CONFIRMED:
            if booking.schedule and booking.schedule.departure_time <= utcnow():
                return False, "This flight has already departed, so it cannot be cancelled."
            return True, "This booking is eligible for cancellation."
        if booking.booking_status in (Booking.STATUS_PENDING, Booking.STATUS_EXPIRED):
            return False, "Only confirmed bookings can be cancelled."
        if booking.booking_status == Booking.STATUS_CANCELLED:
            return False, "This booking has already been cancelled."
        return False, "This booking cannot be cancelled."

    # ------------------------------------------------------------------
    def cancel(self, booking: Booking, reason: str | None = None) -> Cancellation:
        """Cancel a confirmed booking, release seats and record the refund."""
        ok, message = self.eligibility(booking)
        if not ok:
            raise CancellationError(message)

        released = self.repo.release_seats(booking)
        booking.booking_status = Booking.STATUS_CANCELLED
        booking.hold_expires_at = None

        quote = self.refund_quote(booking)
        cancellation = booking.cancellation or Cancellation(booking_id=booking.booking_id)
        cancellation.cancellation_reason = (reason or "Cancelled by passenger").strip()[:255]
        cancellation.refund_amount = quote["refund"]
        cancellation.cancellation_date = utcnow()
        cancellation.refund_status = Cancellation.STATUS_PROCESSED
        cancellation.processed_at = utcnow()
        db.session.add(cancellation)

        if booking.payment and booking.payment.payment_status == Payment.STATUS_SUCCESS:
            booking.payment.payment_status = Payment.STATUS_REFUNDED
            booking.payment.gateway_message = (
                f"Refund of INR {quote['refund']:,.2f} processed "
                f"(cancellation fee INR {quote['fee']:,.2f})."
            )

        db.session.add(booking)
        try:
            db.session.commit()
        except Exception as exc:
            current_app.logger.exception("Cancellation failed: %s", exc)
            db.session.rollback()
            raise

        # Sanity: seats really are free again.
        if released < 0:
            raise CancellationError("Failed to release held seats.")
        return cancellation

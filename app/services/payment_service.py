"""Simulated payment gateway using the Strategy design pattern."""
import secrets
import string
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime

from sqlalchemy import select

from app.extensions import db
from app.models import Booking, Payment
from app.services.booking_service import BookingService
from app.services.ticket_service import TicketService
from app.utils.helpers import utcnow


@dataclass
class PaymentOutcome:
    success: bool
    message: str
    reference: str


@dataclass
class PaymentResult:
    success: bool
    message: str
    booking: object = None
    ticket: object = None
    already_paid: bool = False


class PaymentStrategy(ABC):
    """Abstract mock gateway. Real providers would implement this interface."""

    name = "MOCK"

    @abstractmethod
    def charge(self, amount: float, method: str, reference: str) -> PaymentOutcome:
        ...


class MockSuccessStrategy(PaymentStrategy):
    name = "MOCK_SUCCESS"

    def charge(self, amount: float, method: str, reference: str) -> PaymentOutcome:
        return PaymentOutcome(
            success=True,
            message=f"Payment of INR {amount:,.2f} authorised via {method.lower()}.",
            reference=reference,
        )


class MockFailureStrategy(PaymentStrategy):
    name = "MOCK_FAILURE"

    def charge(self, amount: float, method: str, reference: str) -> PaymentOutcome:
        return PaymentOutcome(
            success=False,
            message="The bank declined this transaction (simulated failure).",
            reference=reference,
        )


class PaymentStrategyFactory:
    """Factory that picks a gateway strategy for the simulated checkout."""

    @staticmethod
    def create(simulate_failure: bool = False) -> PaymentStrategy:
        return MockFailureStrategy() if simulate_failure else MockSuccessStrategy()


class PaymentService:
    def __init__(self, booking_service: BookingService | None = None,
                 ticket_service: TicketService | None = None):
        self.booking_service = booking_service or BookingService()
        self.ticket_service = ticket_service or TicketService()

    @staticmethod
    def _reference() -> str:
        alphabet = string.ascii_uppercase + string.digits
        return "TXN" + "".join(secrets.choice(alphabet) for _ in range(12))

    # ------------------------------------------------------------------
    def process_payment(
        self,
        booking_id: int,
        user,
        method: str = "CARD",
        simulate_failure: bool = False,
    ) -> PaymentResult:
        """Charge the mock gateway exactly once per attempt.

        Safe against duplicate submissions: the booking row is locked and an
        already-successful payment short-circuits without charging twice.
        """
        self.booking_service.expire_stale_holds()

        # Lock the booking row for the duration of the transaction.
        booking = db.session.execute(
            select(Booking).where(Booking.booking_id == booking_id).with_for_update()
        ).scalar_one_or_none()

        if not booking:
            return PaymentResult(False, "Booking not found.")
        if booking.user_id != user.user_id:
            return PaymentResult(False, "You are not allowed to pay for this booking.")

        if booking.booking_status == Booking.STATUS_CONFIRMED:
            return PaymentResult(
                True, "This booking is already paid and confirmed.", booking,
                booking.ticket, already_paid=True,
            )
        if booking.booking_status == Booking.STATUS_CANCELLED:
            return PaymentResult(False, "This booking has been cancelled.")
        if booking.booking_status == Booking.STATUS_EXPIRED or booking.is_hold_expired:
            self.booking_service.repo.release_seats(booking)
            booking.booking_status = Booking.STATUS_EXPIRED
            db.session.commit()
            return PaymentResult(False, "Your seat hold has expired. Please book again.")

        payment = booking.payment
        if payment is None:
            payment = Payment(
                booking_id=booking.booking_id,
                transaction_reference=self._reference(),
                amount=booking.total_amount,
                payment_method=method or "CARD",
                payment_status=Payment.STATUS_PENDING,
            )
            db.session.add(payment)
        else:
            # Retry keeps the same reference but records a new attempt.
            payment.payment_method = method or payment.payment_method

        payment.attempts = (payment.attempts or 0) + 1
        payment.amount = booking.total_amount
        strategy = PaymentStrategyFactory.create(simulate_failure)
        outcome = strategy.charge(float(booking.total_amount), payment.payment_method, payment.transaction_reference)
        payment.gateway_message = outcome.message
        payment.payment_time = utcnow()

        if outcome.success:
            payment.payment_status = Payment.STATUS_SUCCESS
            self.booking_service.confirm_booking(booking)
            db.session.flush()
            ticket = self.ticket_service.generate_for_booking(booking)
            db.session.commit()
            return PaymentResult(True, outcome.message, booking, ticket, already_paid=False)

        # Failure: record it, keep the booking PENDING so the hold stays valid.
        payment.payment_status = Payment.STATUS_FAILED
        db.session.commit()
        return PaymentResult(False, outcome.message, booking, None)

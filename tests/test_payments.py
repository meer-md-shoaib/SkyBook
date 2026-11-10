"""Payment success, failure, retry and idempotency tests."""
import os

from app.extensions import db
from app.models import Booking, Payment, Ticket
from app.services.payment_service import PaymentService


def test_failed_payment_keeps_booking_pending(
    app, passenger, schedule, available_seats, make_booking
):
    booking = make_booking(passenger, schedule, available_seats[:1])

    result = PaymentService().process_payment(
        booking.booking_id, passenger, method="CARD", simulate_failure=True
    )

    assert result.success is False
    db.session.refresh(booking)
    assert booking.booking_status == Booking.STATUS_PENDING
    assert booking.payment.payment_status == Payment.STATUS_FAILED
    assert booking.payment.attempts == 1


def test_retry_after_failure_confirms_booking_and_generates_ticket(
    app, passenger, schedule, available_seats, make_booking
):
    booking = make_booking(passenger, schedule, available_seats[:1])
    service = PaymentService()

    service.process_payment(booking.booking_id, passenger, simulate_failure=True)
    result = service.process_payment(booking.booking_id, passenger, method="UPI")

    assert result.success is True
    db.session.refresh(booking)
    assert booking.booking_status == Booking.STATUS_CONFIRMED
    assert booking.payment.payment_status == Payment.STATUS_SUCCESS
    assert booking.payment.attempts == 2

    ticket = Ticket.query.filter_by(booking_id=booking.booking_id).first()
    assert ticket is not None
    assert ticket.file_path
    assert os.path.exists(os.path.join(app.config["TICKET_OUTPUT_DIR"], ticket.file_path))

    # Seats are now BOOKED, not merely held.
    for seat in booking.active_seats:
        assert seat.status == "BOOKED"


def test_successful_payment_is_idempotent(
    app, passenger, schedule, available_seats, make_booking
):
    booking = make_booking(passenger, schedule, available_seats[:1])
    service = PaymentService()

    first = service.process_payment(booking.booking_id, passenger)
    second = service.process_payment(booking.booking_id, passenger)

    assert first.success and not first.already_paid
    assert second.success and second.already_paid
    db.session.refresh(booking)
    assert booking.payment.attempts == 1


def test_payment_rejects_other_users_booking(
    app, passenger, other_passenger, schedule, available_seats, make_booking
):
    booking = make_booking(passenger, schedule, available_seats[:1])
    result = PaymentService().process_payment(booking.booking_id, other_passenger)
    assert result.success is False
    assert "not allowed" in result.message


def test_gateway_callback_is_idempotent(
    client, app, passenger, schedule, available_seats, make_booking
):
    booking = make_booking(passenger, schedule, available_seats[:1])
    PaymentService().process_payment(booking.booking_id, passenger)
    reference = booking.payment.transaction_reference

    first = client.post("/payments/callback", json={"transaction_reference": reference})
    second = client.post("/payments/callback", json={"transaction_reference": reference})

    assert first.status_code == 200
    assert first.get_json()["duplicate"] is True
    assert second.get_json()["duplicate"] is True


def test_callback_rejects_unknown_reference(client, app):
    response = client.post("/payments/callback", json={"transaction_reference": "TXNUNKNOWN"})
    assert response.status_code == 404


def test_payment_on_expired_hold_fails(app, passenger, schedule, available_seats, make_booking):
    from datetime import timedelta
    from app.utils.helpers import utcnow

    booking = make_booking(passenger, schedule, available_seats[:1])
    booking.hold_expires_at = utcnow() - timedelta(minutes=5)
    db.session.commit()

    result = PaymentService().process_payment(booking.booking_id, passenger)
    assert result.success is False
    assert "expired" in result.message.lower()


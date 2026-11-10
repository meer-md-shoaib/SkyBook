"""Cancellation eligibility, seat release and refund tests."""
import pytest

from app.extensions import db
from app.models import Booking, Cancellation, Payment, Seat
from app.services.cancellation_service import CancellationError, CancellationService
from app.services.payment_service import PaymentService


def test_pending_booking_is_not_cancellable(
    app, passenger, schedule, available_seats, make_booking
):
    booking = make_booking(passenger, schedule, available_seats[:1])
    eligible, reason = CancellationService.eligibility(booking)
    assert eligible is False
    assert "confirmed" in reason.lower()


def test_confirmed_booking_cancellation_releases_seats_and_refunds(
    app, passenger, schedule, available_seats, make_booking
):
    booking = make_booking(passenger, schedule, available_seats[:2])
    PaymentService().process_payment(booking.booking_id, passenger)
    db.session.refresh(booking)

    eligible, _ = CancellationService.eligibility(booking)
    assert eligible is True

    quote = CancellationService.refund_quote(booking)
    cancellation = CancellationService().cancel(booking, "Change of plans")
    db.session.refresh(booking)

    assert booking.booking_status == Booking.STATUS_CANCELLED
    assert cancellation.refund_status == Cancellation.STATUS_PROCESSED
    assert float(cancellation.refund_amount) == pytest.approx(quote["refund"])
    # 10% cancellation fee is retained by default.
    assert float(cancellation.refund_amount) == pytest.approx(float(booking.total_amount) * 0.9, rel=0.01)

    for seat in available_seats[:2]:
        db.session.refresh(seat)
        assert seat.status == Seat.STATUS_AVAILABLE
        assert seat.current_booking_id is None

    assert booking.payment.payment_status == Payment.STATUS_REFUNDED


def test_booking_cannot_be_cancelled_twice(
    app, passenger, schedule, available_seats, make_booking
):
    booking = make_booking(passenger, schedule, available_seats[:1])
    PaymentService().process_payment(booking.booking_id, passenger)
    service = CancellationService()
    service.cancel(booking)

    with pytest.raises(CancellationError, match="already been cancelled"):
        service.cancel(booking)


def test_cancel_route_requires_confirmation(
    client, login, passenger, schedule, available_seats, make_booking
):
    booking = make_booking(passenger, schedule, available_seats[:1])
    PaymentService().process_payment(booking.booking_id, passenger)
    login("demo@skybook.com", "Passenger@123")

    response = client.post(f"/bookings/{booking.booking_id}/cancel", data={}, follow_redirects=True)
    assert b"confirm the cancellation" in response.data
    db.session.refresh(booking)
    assert booking.booking_status == Booking.STATUS_CONFIRMED


def test_cannot_cancel_pending_booking(app, passenger, schedule, available_seats, make_booking):
    booking = make_booking(passenger, schedule, available_seats[:1])
    service = CancellationService()
    with pytest.raises(CancellationError, match="Only confirmed bookings"):
        service.cancel(booking)


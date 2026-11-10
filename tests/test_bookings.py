"""Seat-hold, passenger validation and access-control tests."""
import pytest

from app.extensions import db
from app.models import Booking, Seat
from app.services.booking_service import BookingError, BookingService


def test_seat_hold_creates_pending_booking(app, passenger, schedule, available_seats):
    booking = BookingService().create_pending_booking(
        user=passenger,
        schedule_id=schedule.schedule_id,
        seat_ids=[seat.seat_id for seat in available_seats[:2]],
        contact_email=passenger.email,
        contact_phone=passenger.phone,
    )
    assert booking.booking_status == Booking.STATUS_PENDING
    assert booking.total_amount > 0
    assert len(booking.active_seats) == 2
    for seat in booking.active_seats:
        assert seat.status == Seat.STATUS_HELD
        assert seat.current_booking_id == booking.booking_id


def test_duplicate_seat_submission_is_rejected(app, passenger, schedule, available_seats):
    seat_id = available_seats[0].seat_id
    with pytest.raises(BookingError, match="Duplicate seats"):
        BookingService().create_pending_booking(
            user=passenger,
            schedule_id=schedule.schedule_id,
            seat_ids=[seat_id, seat_id],
            contact_email=passenger.email,
            contact_phone=passenger.phone,
        )


def test_already_held_seat_cannot_be_booked_again(
    app, passenger, other_passenger, schedule, available_seats, make_booking
):
    make_booking(passenger, schedule, available_seats[:1])

    with pytest.raises(BookingError, match="just taken|reserved"):
        BookingService().create_pending_booking(
            user=other_passenger,
            schedule_id=schedule.schedule_id,
            seat_ids=[available_seats[0].seat_id],
            contact_email=other_passenger.email,
            contact_phone=other_passenger.phone,
        )


def test_invalid_passenger_details_are_rejected(
    app, passenger, schedule, available_seats, make_booking
):
    booking = make_booking(passenger, schedule, available_seats[:1], with_passengers=False)
    errors = BookingService().save_passengers(
        booking,
        [
            {
                "full_name": "X",
                "date_of_birth": "2999-01-01",
                "gender": "UNKNOWN",
                "identification_type": "NOPE",
                "identification_number": "!",
            }
        ],
    )
    assert errors
    assert len(booking.passengers) == 0


def test_passenger_count_must_match_seats(
    app, passenger, schedule, available_seats, make_booking
):
    booking = make_booking(passenger, schedule, available_seats[:2], with_passengers=False)
    errors = BookingService().save_passengers(
        booking,
        [
            {
                "full_name": "Solo Traveller",
                "date_of_birth": "1990-01-01",
                "gender": "MALE",
                "identification_type": "PASSPORT",
                "identification_number": "M1234567",
            }
        ],
    )
    assert errors
    assert any("exactly 2" in error for error in errors)


def test_expired_hold_releases_seats(
    app, passenger, schedule, available_seats, make_booking
):
    from datetime import timedelta
    from app.utils.helpers import utcnow

    booking = make_booking(passenger, schedule, available_seats[:1])
    booking.hold_expires_at = utcnow() - timedelta(minutes=1)
    db.session.commit()

    released = BookingService().expire_stale_holds()

    assert released == 1
    db.session.refresh(booking)
    db.session.refresh(available_seats[0])
    assert booking.booking_status == Booking.STATUS_EXPIRED
    assert available_seats[0].status == Seat.STATUS_AVAILABLE


def test_other_user_cannot_view_booking(
    client, login, passenger, other_passenger, schedule, available_seats, make_booking
):
    booking = make_booking(passenger, schedule, available_seats[:1])
    login("riya@example.com", "Passenger@123")

    response = client.get(f"/bookings/{booking.booking_id}")
    assert response.status_code == 404


def test_anonymous_user_is_redirected_to_login(client, passenger, schedule, available_seats, make_booking):
    booking = make_booking(passenger, schedule, available_seats[:1])
    response = client.get(f"/bookings/{booking.booking_id}")
    assert response.status_code == 302
    assert "/auth/login" in response.headers["Location"]


def test_hold_route_creates_booking_and_redirects(
    client, login, passenger, schedule, available_seats
):
    login("demo@skybook.com", "Passenger@123")
    response = client.post(
        f"/flights/{schedule.schedule_id}/seats/hold",
        data={"seat_ids": [available_seats[0].seat_id]},
    )
    assert response.status_code == 302
    assert "/passengers" in response.headers["Location"]


def test_max_seats_exceeded_raises_error(passenger, schedule, available_seats, app):
    import pytest
    from app.services.booking_service import BookingError, BookingService
    from app.models import Booking, Seat

    all_seats = (
        Seat.query.filter_by(schedule_id=schedule.schedule_id, status=Seat.STATUS_AVAILABLE)
        .limit(7)
        .all()
    )
    if len(all_seats) >= 7:
        with pytest.raises(BookingError, match="at most 6 seats"):
            BookingService().create_pending_booking(
                user=passenger,
                schedule_id=schedule.schedule_id,
                seat_ids=[s.seat_id for s in all_seats],
            )
        assert Booking.query.filter_by(user_id=passenger.user_id, booking_status="PENDING").count() == 0

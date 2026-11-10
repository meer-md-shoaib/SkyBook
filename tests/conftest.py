"""Pytest fixtures: a seeded application bound to the test database."""
from datetime import datetime

import pytest
from dotenv import load_dotenv

load_dotenv()

from app import create_app
from app.extensions import db
from app.models import Booking, FlightSchedule, Seat, User
from app.seed import seed_database
from app.services.booking_service import BookingService
from app.utils.helpers import utcnow


@pytest.fixture()
def app(tmp_path):
    """Fresh schema + demo data for every test (CSRF disabled)."""
    application = create_app("testing")
    application.config["TICKET_OUTPUT_DIR"] = str(tmp_path / "tickets")
    with application.app_context():
        db.drop_all()
        db.create_all()
        seed_database(days=2)
        yield application
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def login(client):
    def _login(email: str, password: str):
        return client.post(
            "/auth/login",
            data={"email": email, "password": password},
            follow_redirects=True,
        )

    return _login


@pytest.fixture()
def passenger(app):
    return User.query.filter_by(email="demo@skybook.com").first()


@pytest.fixture()
def other_passenger(app):
    return User.query.filter_by(email="riya@example.com").first()


@pytest.fixture()
def admin(app):
    return User.query.filter_by(email="admin@skybook.com").first()


@pytest.fixture()
def schedule(app):
    """The soonest future schedule with free seats."""
    return (
        FlightSchedule.query.filter(FlightSchedule.departure_time > utcnow())
        .order_by(FlightSchedule.departure_time.asc())
        .first()
    )


@pytest.fixture()
def available_seats(app, schedule):
    return (
        Seat.query.filter_by(schedule_id=schedule.schedule_id, status=Seat.STATUS_AVAILABLE)
        .order_by(Seat.seat_id.asc())
        .limit(4)
        .all()
    )


NAMES = ("Aarav Sharma", "Ananya Menon", "Rohan Gupta", "Isha Nair")


def _passenger_payload(index: int = 0) -> dict:
    return {
        "full_name": NAMES[index % len(NAMES)],
        "date_of_birth": "1990-01-0%d" % (index + 1),
        "gender": "MALE" if index % 2 == 0 else "FEMALE",
        "identification_type": "AADHAAR",
        "identification_number": "12345678901%d" % index,
    }


@pytest.fixture()
def make_booking(app):
    """Create a PENDING booking with passenger details via the real service."""

    def _make(user, flight_schedule, seats, with_passengers: bool = True) -> Booking:
        service = BookingService()
        booking = service.create_pending_booking(
            user=user,
            schedule_id=flight_schedule.schedule_id,
            seat_ids=[seat.seat_id for seat in seats],
            contact_email=user.email,
            contact_phone=user.phone,
        )
        if with_passengers:
            errors = service.save_passengers(
                booking, [_passenger_payload(i) for i in range(len(seats))]
            )
            assert not errors, errors
        return booking

    return _make

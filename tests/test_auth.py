"""Authentication and role-based access tests."""
from app.models import User


def test_register_creates_passenger(client, app):
    response = client.post(
        "/auth/register",
        data={
            "name": "New Traveller",
            "email": "new.traveller@example.com",
            "phone": "+91 90000 22222",
            "password": "Skybook123",
            "confirm_password": "Skybook123",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    user = User.query.filter_by(email="new.traveller@example.com").first()
    assert user is not None
    assert user.role == User.ROLE_PASSENGER
    assert user.check_password("Skybook123")


def test_login_with_wrong_password_fails(client, app):
    response = client.post(
        "/auth/login",
        data={"email": "demo@skybook.com", "password": "wrong-password"},
        follow_redirects=True,
    )
    assert b"Incorrect email or password" in response.data


def test_login_succeeds_for_seeded_passenger(client, login):
    response = login("demo@skybook.com", "Passenger@123")
    assert b"Signed in as" in response.data


def test_passenger_cannot_reach_admin_area(client, login):
    login("demo@skybook.com", "Passenger@123")
    response = client.get("/admin/", follow_redirects=False)
    assert response.status_code == 302
    assert response.headers["Location"].endswith("/")


def test_admin_can_reach_dashboard(client, login):
    login("admin@skybook.com", "Admin@123")
    response = client.get("/admin/")
    assert response.status_code == 200
    assert b"Dashboard" in response.data


def test_logout_clears_session(client, login):
    login("demo@skybook.com", "Passenger@123")
    response = client.post("/auth/logout", follow_redirects=True)
    assert b"signed out" in response.data
    # The bookings area is now protected again.
    assert client.get("/bookings/").status_code == 302


def test_register_weak_password_fails(client, app):
    response = client.post(
        "/auth/register",
        data={
            "name": "Weak User",
            "email": "weak@example.com",
            "phone": "+91 90000 22222",
            "password": "weakpassword",
            "confirm_password": "weakpassword",
        },
        follow_redirects=True,
    )
    assert b"Password must be at least 8 characters" in response.data


def test_register_duplicate_email_fails(client, app):
    response = client.post(
        "/auth/register",
        data={
            "name": "Duplicate Demo",
            "email": "demo@skybook.com",
            "phone": "+91 90000 22222",
            "password": "Password@123",
            "confirm_password": "Password@123",
        },
        follow_redirects=True,
    )
    assert b"already exists" in response.data


def test_admin_flights_page(client, login):
    login("admin@skybook.com", "Admin@123")
    response = client.get("/admin/flights")
    assert response.status_code == 200
    assert b"Flights" in response.data


def test_admin_create_and_toggle_flight(client, login):
    login("admin@skybook.com", "Admin@123")
    # Source 1 (BLR), Destination 2 (DEL)
    response = client.post(
        "/admin/flights/new",
        data={
            "flight_number": "SB 999",
            "airline_name": "SkyBook Express",
            "source_airport_id": 1,
            "destination_airport_id": 2,
            "aircraft_type": "Boeing 737",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert b"added" in response.data or b"SB 999" in response.data

    from app.models import Flight
    flt = Flight.query.filter_by(flight_number="SB 999").first()
    assert flt is not None
    assert flt.is_active is True

    # Toggle flight
    response = client.post(f"/admin/flights/{flt.flight_id}/toggle", follow_redirects=True)
    assert response.status_code == 200
    assert flt.is_active is False


def test_admin_schedules_and_reports_pages(client, login):
    login("admin@skybook.com", "Admin@123")

    assert client.get("/admin/schedules").status_code == 200
    assert client.get("/admin/bookings").status_code == 200
    assert client.get("/admin/passengers").status_code == 200
    assert client.get("/admin/payments").status_code == 200
    assert client.get("/admin/cancellations").status_code == 200


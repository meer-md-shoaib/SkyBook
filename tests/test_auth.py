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
    response = client.get("/auth/logout", follow_redirects=True)
    assert b"signed out" in response.data
    # The bookings area is now protected again.
    assert client.get("/bookings/").status_code == 302

"""Flight search validation and filtering tests."""
from datetime import date, timedelta

from app.services.flight_service import FlightService

TOMORROW = (date.today() + timedelta(days=1)).isoformat()
YESTERDAY = (date.today() - timedelta(days=1)).isoformat()


def test_search_returns_matching_db_records(app):
    outcome = FlightService().search("Bengaluru", "Delhi", TOMORROW, passengers=1)
    assert outcome["errors"] == []
    assert outcome["flights"], "expected at least one BLR -> DEL schedule"
    for schedule in outcome["flights"]:
        assert schedule.flight.source_airport.city == "Bengaluru"
        assert schedule.flight.destination_airport.city == "Delhi"


def test_search_with_no_matching_route_is_empty(app):
    outcome = FlightService().search("Kochi", "Delhi", TOMORROW, passengers=1)
    assert outcome["errors"] == []
    assert outcome["flights"] == []


def test_same_city_search_is_rejected(app):
    outcome = FlightService().search("Delhi", "Delhi", TOMORROW, passengers=1)
    assert outcome["flights"] == []
    assert any("must be different" in error for error in outcome["errors"])


def test_past_travel_date_is_rejected(app):
    outcome = FlightService().search("Bengaluru", "Delhi", YESTERDAY, passengers=1)
    assert outcome["flights"] == []
    assert any("past" in error for error in outcome["errors"])


def test_invalid_date_is_rejected(app):
    outcome = FlightService().search("Bengaluru", "Delhi", "not-a-date", passengers=1)
    assert outcome["flights"] == []
    assert any("valid date" in error for error in outcome["errors"])


def test_passenger_count_is_clamped(app):
    outcome = FlightService().search("Bengaluru", "Delhi", TOMORROW, passengers=99)
    assert outcome["criteria"]["passengers"] == 6


def test_results_page_renders(client, login):
    login("demo@skybook.com", "Passenger@123")
    response = client.get(
        f"/flights/results?source=Bengaluru&destination=Delhi&date={TOMORROW}&passengers=1"
    )
    assert response.status_code == 200
    assert b"Bengaluru" in response.data

"""Flight search and seat-map business logic."""
from datetime import date

from app.models import Seat
from app.repositories.flight_repository import FlightRepository
from app.utils.helpers import parse_iso_date


class FlightService:
    def __init__(self, repo: FlightRepository | None = None):
        self.repo = repo or FlightRepository()

    # ---- lookups ----------------------------------------------------------
    def cities(self):
        """Return all available airports/cities for route dropdowns."""
        return self.repo.list_airports()

    def airlines(self) -> list[str]:
        return self.repo.list_airlines()

    def schedules(self):
        return self.repo.upcoming_schedules()

    # ---- search -----------------------------------------------------------
    def search(
        self,
        source: str | None,
        destination: str | None,
        travel_date: str | None,
        passengers: int = 1,
        airline: str | None = None,
        max_price: str | None = None,
        departure_window: str | None = None,
    ) -> dict:
        """Validate search input and return ``{"flights", "errors", "criteria"}``."""
        errors: list[str] = []
        source = (source or "").strip()
        destination = (destination or "").strip()
        parsed_date = parse_iso_date(travel_date)

        if not source:
            errors.append("Please choose a departure city.")
        if not destination:
            errors.append("Please choose a destination city.")
        if source and destination and source.lower() == destination.lower():
            errors.append("Departure and destination cities must be different.")
        if travel_date and not parsed_date:
            errors.append("Travel date must be a valid date (YYYY-MM-DD).")
        if parsed_date and parsed_date < date.today():
            errors.append("Travel date cannot be in the past.")
        try:
            passengers = max(1, min(int(passengers or 1), 6))
        except (TypeError, ValueError):
            passengers = 1

        price_limit = None
        if max_price:
            try:
                price_limit = float(max_price)
            except (TypeError, ValueError):
                price_limit = None

        criteria = {
            "source": source,
            "destination": destination,
            "travel_date": travel_date or "",
            "passengers": passengers,
            "airline": airline or "",
            "max_price": max_price or "",
            "departure_window": departure_window or "",
        }

        if errors:
            return {"flights": [], "errors": errors, "criteria": criteria}

        flights = self.repo.search_schedules(
            source_city=source,
            destination_city=destination,
            travel_date=parsed_date,
            airline=airline or None,
            max_price=price_limit,
            departure_window=departure_window or None,
        )
        # Only keep schedules with enough free seats for the party.
        flights = [f for f in flights if f.available_seats >= passengers]
        return {"flights": flights, "errors": [], "criteria": criteria}

    # ---- detail / seat map ------------------------------------------------
    def get_schedule(self, schedule_id: int):
        return self.repo.get_schedule(schedule_id)

    def seat_map(self, schedule_id: int) -> dict:
        """Build the payload consumed by the interactive seat map."""
        schedule = self.repo.get_schedule(schedule_id)
        if not schedule:
            return {}
        seats = self.repo.get_schedule_seats(schedule_id)
        rows: dict[int, dict] = {}
        for seat in seats:
            row = rows.setdefault(
                seat.seat_row,
                {"number": seat.seat_row, "seat_class": seat.seat_class, "seats": {}},
            )
            row["seats"][seat.seat_column] = {
                "id": seat.seat_id,
                "number": seat.seat_number,
                "status": seat.status,
                "class": seat.seat_class,
                "price": schedule.seat_price(seat.seat_class),
            }
        ordered = []
        for number in sorted(rows):
            row = rows[number]
            ordered.append(
                {
                    "number": row["number"],
                    "seat_class": row["seat_class"],
                    "columns": [row["seats"].get(c) for c in "ABCDEF"],
                }
            )
        counts = {
            "available": sum(1 for s in seats if s.status == Seat.STATUS_AVAILABLE),
            "occupied": sum(1 for s in seats if s.status != Seat.STATUS_AVAILABLE),
            "total": len(seats),
        }
        return {"schedule": schedule, "rows": ordered, "counts": counts}

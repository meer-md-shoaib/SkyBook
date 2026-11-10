"""Data access for airports, flights and schedules."""
from datetime import date, datetime, time, timedelta

from sqlalchemy.orm import aliased

from app.extensions import db
from app.models import Airport, Flight, FlightSchedule, Seat


class FlightRepository:
    # ---- airports ---------------------------------------------------------
    @staticmethod
    def list_airports():
        return Airport.query.order_by(Airport.city.asc()).all()

    @staticmethod
    def list_cities():
        rows = db.session.query(Airport.city).distinct().order_by(Airport.city.asc()).all()
        return [row[0] for row in rows]

    @staticmethod
    def get_airport(airport_id: int) -> Airport | None:
        return db.session.get(Airport, airport_id)

    # ---- schedules --------------------------------------------------------
    @staticmethod
    def search_schedules(
        source_city: str | None = None,
        destination_city: str | None = None,
        travel_date: date | None = None,
        airline: str | None = None,
        max_price: float | None = None,
        departure_window: str | None = None,
        only_available: bool = True,
    ):
        """Return schedules matching the route/date with optional filters."""
        src = aliased(Airport)
        dst = aliased(Airport)

        query = (
            db.session.query(FlightSchedule)
            .join(Flight, FlightSchedule.flight_id == Flight.flight_id)
            .join(src, Flight.source_airport_id == src.airport_id)
            .join(dst, Flight.destination_airport_id == dst.airport_id)
            .filter(Flight.is_active.is_(True))
            .filter(FlightSchedule.status == FlightSchedule.STATUS_SCHEDULED)
        )

        if source_city:
            query = query.filter(src.city.ilike(source_city.strip()))
        if destination_city:
            query = query.filter(dst.city.ilike(destination_city.strip()))
        if travel_date:
            start = datetime.combine(travel_date, time.min)
            query = query.filter(
                FlightSchedule.departure_time >= start,
                FlightSchedule.departure_time < start + timedelta(days=1),
            )
        else:
            query = query.filter(FlightSchedule.departure_time >= datetime.utcnow())
        if airline:
            query = query.filter(Flight.airline_name == airline)
        if max_price:
            query = query.filter(FlightSchedule.base_fare <= max_price)
        if departure_window:
            windows = {
                "morning": (5, 12),
                "afternoon": (12, 17),
                "evening": (17, 21),
                "night": (21, 24),
            }
            if departure_window in windows:
                start_h, end_h = windows[departure_window]
                day = travel_date or date.today()
                window_start = datetime.combine(day, time(hour=start_h))
                window_end = window_start + timedelta(hours=end_h - start_h)
                query = query.filter(
                    FlightSchedule.departure_time >= window_start,
                    FlightSchedule.departure_time < window_end,
                )

        schedules = query.order_by(FlightSchedule.departure_time.asc()).all()
        if only_available:
            schedules = [s for s in schedules if s.available_seats > 0]
        return schedules

    @staticmethod
    def get_schedule(schedule_id: int) -> FlightSchedule | None:
        return db.session.get(FlightSchedule, int(schedule_id))

    @staticmethod
    def get_schedule_seats(schedule_id: int):
        return (
            Seat.query.filter_by(schedule_id=schedule_id)
            .order_by(Seat.seat_row.asc(), Seat.seat_column.asc())
            .all()
        )

    @staticmethod
    def list_airlines():
        rows = (
            db.session.query(Flight.airline_name)
            .distinct()
            .order_by(Flight.airline_name.asc())
            .all()
        )
        return [row[0] for row in rows]

    @staticmethod
    def list_flights():
        return Flight.query.order_by(Flight.flight_number.asc()).all()

    @staticmethod
    def upcoming_schedules(limit: int = 8):
        return (
            FlightSchedule.query.filter(
                FlightSchedule.departure_time >= datetime.utcnow(),
                FlightSchedule.status == FlightSchedule.STATUS_SCHEDULED,
            )
            .order_by(FlightSchedule.departure_time.asc())
            .limit(limit)
            .all()
        )

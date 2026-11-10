"""Demo data seeder for SkyBook.

Creates Indian airports, airlines, routes, 10 days of schedules, full seat
inventories and demo accounts (one administrator, two passengers).
"""
from datetime import date, datetime, time, timedelta

from app.extensions import db
from app.models import (
    Airport, Booking, BookingSeat, Flight, FlightSchedule, Passenger, Payment, Seat, Ticket, User,
)
from app.services.ticket_service import TicketService
from app.utils.helpers import utcnow

AIRPORTS = [
    ("BLR", "Kempegowda International Airport", "Bengaluru"),
    ("DEL", "Indira Gandhi International Airport", "Delhi"),
    ("BOM", "Chhatrapati Shivaji Maharaj International Airport", "Mumbai"),
    ("HYD", "Rajiv Gandhi International Airport", "Hyderabad"),
    ("MAA", "Chennai International Airport", "Chennai"),
    ("COK", "Cochin International Airport", "Kochi"),
]

# (flight_number, airline, source, destination, aircraft, departure hour, minute, duration mins, fare)
ROUTES = [
    # Bengaluru <-> Delhi (3 options each way)
    ("6E 204", "IndiGo", "BLR", "DEL", "Airbus A320neo", 6, 15, 165, 5499),
    ("AI 502", "Air India", "BLR", "DEL", "Boeing 787-8", 11, 30, 160, 6199),
    ("UK 812", "Vistara", "BLR", "DEL", "Airbus A321neo", 18, 45, 155, 5899),
    ("6E 534", "IndiGo", "DEL", "BLR", "Airbus A320neo", 8, 30, 165, 5399),
    ("AI 503", "Air India", "DEL", "BLR", "Boeing 787-8", 15, 20, 160, 6099),
    ("UK 819", "Vistara", "DEL", "BLR", "Airbus A321neo", 20, 10, 155, 5999),

    # Delhi <-> Mumbai (3 options each way)
    ("AI 505", "Air India", "DEL", "BOM", "Boeing 737 MAX", 8, 40, 130, 6299),
    ("6E 2112", "IndiGo", "DEL", "BOM", "Airbus A320neo", 13, 15, 125, 5199),
    ("UK 975", "Vistara", "DEL", "BOM", "Airbus A321neo", 17, 30, 125, 6599),
    ("AI 806", "Air India", "BOM", "DEL", "Boeing 787-8", 9, 0, 125, 6899),
    ("6E 2445", "IndiGo", "BOM", "DEL", "Airbus A320", 14, 40, 130, 5299),
    ("UK 996", "Vistara", "BOM", "DEL", "Airbus A321neo", 19, 15, 125, 6499),

    # Mumbai <-> Bengaluru (3 options each way)
    ("UK 945", "Vistara", "BOM", "BLR", "Airbus A320neo", 10, 5, 105, 4899),
    ("6E 5184", "IndiGo", "BOM", "BLR", "Airbus A320", 14, 50, 100, 4299),
    ("QP 1102", "Akasa Air", "BOM", "BLR", "Boeing 737 MAX", 19, 20, 105, 3999),
    ("UK 831", "Vistara", "BLR", "BOM", "Airbus A321neo", 19, 45, 100, 4699),
    ("6E 374", "IndiGo", "BLR", "BOM", "Airbus A320neo", 7, 10, 105, 4399),
    ("QP 1108", "Akasa Air", "BLR", "BOM", "Boeing 737 MAX", 12, 40, 105, 3899),

    # Hyderabad <-> Chennai (3 options each way)
    ("SG 721", "SpiceJet", "HYD", "MAA", "Boeing 737-800", 12, 30, 80, 3199),
    ("6E 714", "IndiGo", "HYD", "MAA", "Airbus A320", 8, 15, 75, 3399),
    ("AI 542", "Air India", "HYD", "MAA", "Airbus A320neo", 18, 50, 80, 3699),
    ("SG 305", "SpiceJet", "MAA", "HYD", "Boeing 737-800", 7, 25, 85, 2999),
    ("6E 719", "IndiGo", "MAA", "HYD", "Airbus A320neo", 14, 10, 80, 3299),
    ("AI 547", "Air India", "MAA", "HYD", "Airbus A320", 21, 0, 80, 3599),

    # Kochi <-> Bengaluru (3 options each way)
    ("QP 1105", "Akasa Air", "COK", "BLR", "Boeing 737 MAX", 14, 20, 70, 2899),
    ("6E 478", "IndiGo", "COK", "BLR", "Airbus A320", 9, 30, 65, 2799),
    ("AI 511", "Air India", "COK", "BLR", "Airbus A320neo", 19, 0, 70, 3199),
    ("6E 471", "IndiGo", "BLR", "COK", "Airbus A320", 21, 15, 65, 2699),
    ("QP 1109", "Akasa Air", "BLR", "COK", "Boeing 737 MAX", 7, 45, 70, 2849),
    ("AI 514", "Air India", "BLR", "COK", "Airbus A320neo", 13, 30, 70, 3099),

    # Cross connections: Delhi, Hyderabad, Chennai
    ("6E 618", "IndiGo", "DEL", "HYD", "Airbus A320", 16, 0, 125, 4599),
    ("AI 839", "Air India", "DEL", "HYD", "Airbus A321neo", 10, 15, 120, 4899),
    ("QP 1302", "Akasa Air", "HYD", "BLR", "Boeing 737 MAX", 13, 10, 75, 3099),
    ("6E 498", "IndiGo", "HYD", "BLR", "Airbus A320neo", 7, 50, 75, 2999),
    ("AI 439", "Air India", "MAA", "DEL", "Airbus A321neo", 18, 10, 145, 5999),
    ("6E 2134", "IndiGo", "MAA", "DEL", "Airbus A320neo", 6, 40, 150, 5299),
]

BUSINESS_COLUMNS = ("A", "C", "D", "F")
ECONOMY_COLUMNS = ("A", "B", "C", "D", "E", "F")


def _seed_airports() -> dict:
    airports = {}
    for code, name, city in AIRPORTS:
        airport = Airport.query.filter_by(airport_code=code).first()
        if not airport:
            airport = Airport(
                airport_code=code, airport_name=name, city=city, country="India"
            )
            db.session.add(airport)
            db.session.flush()
        airports[code] = airport
    return airports


def _seat_payload(schedule_id: int, business_rows: int, economy_rows: int) -> list[dict]:
    rows = []
    for row in range(1, business_rows + 1):
        for column in BUSINESS_COLUMNS:
            rows.append(
                {
                    "schedule_id": schedule_id,
                    "seat_number": f"{row}{column}",
                    "seat_class": "BUSINESS",
                    "seat_row": row,
                    "seat_column": column,
                    "status": "AVAILABLE",
                }
            )
    for row in range(business_rows + 1, business_rows + economy_rows + 1):
        for column in ECONOMY_COLUMNS:
            rows.append(
                {
                    "schedule_id": schedule_id,
                    "seat_number": f"{row}{column}",
                    "seat_class": "ECONOMY",
                    "seat_row": row,
                    "seat_column": column,
                    "status": "AVAILABLE",
                }
            )
    return rows


def _seed_users() -> dict:
    users = {}
    specs = [
        ("SkyBook Administrator", "admin@skybook.com", "Admin@123", "+91 90000 11111", "ADMIN"),
        ("Demo Passenger", "demo@skybook.com", "Passenger@123", "+91 98765 43210", "PASSENGER"),
        ("Riya Menon", "riya@example.com", "Passenger@123", "+91 91234 56789", "PASSENGER"),
    ]
    for name, email, password, phone, role in specs:
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=name, email=email, phone=phone, role=role)
            user.set_password(password)
            db.session.add(user)
        users[email] = user
    db.session.flush()
    return users


def _seed_flights(airports: dict) -> list[Flight]:
    flights = []
    for number, airline, src, dst, aircraft, *_ in ROUTES:
        flight = Flight.query.filter_by(flight_number=number).first()
        if not flight:
            flight = Flight(
                flight_number=number,
                airline_name=airline,
                source_airport_id=airports[src].airport_id,
                destination_airport_id=airports[dst].airport_id,
                aircraft_type=aircraft,
                is_active=True,
            )
            db.session.add(flight)
            db.session.flush()
        flights.append(flight)
    return flights


def _seed_schedules(flights: list[Flight], days: int = 10) -> None:
    today = date.today()
    for day_offset in range(days):
        travel_day = today + timedelta(days=day_offset)
        for flight, spec in zip(flights, ROUTES):
            _, _, _, _, _, hour, minute, duration, fare = spec
            departure = datetime.combine(travel_day, time(hour=hour, minute=minute))
            existing = FlightSchedule.query.filter_by(
                flight_id=flight.flight_id, departure_time=departure
            ).first()
            if existing:
                continue
            schedule = FlightSchedule(
                flight_id=flight.flight_id,
                departure_time=departure,
                arrival_time=departure + timedelta(minutes=duration),
                base_fare=fare,
                status=FlightSchedule.STATUS_SCHEDULED,
            )
            db.session.add(schedule)
            db.session.flush()
            db.session.bulk_insert_mappings(
                Seat, _seat_payload(schedule.schedule_id, business_rows=3, economy_rows=20)
            )


def _seed_demo_booking(users: dict) -> None:
    """One confirmed booking so the dashboards/tickets are demonstrable."""
    if Booking.query.count() > 0:
        return
    schedule = (
        FlightSchedule.query.join(Flight)
        .filter(
            Flight.flight_number == "6E 204",
            FlightSchedule.departure_time >= utcnow() + timedelta(hours=6),
        )
        .order_by(FlightSchedule.departure_time.asc())
        .first()
    )
    if not schedule:
        return

    user = users["demo@skybook.com"]
    seats = (
        Seat.query.filter_by(schedule_id=schedule.schedule_id, seat_class="ECONOMY")
        .order_by(Seat.seat_row.asc(), Seat.seat_column.asc())
        .limit(2)
        .all()
    )
    if len(seats) < 2:
        return

    total = round(sum(schedule.seat_price(s.seat_class) for s in seats), 2)
    booking = Booking(
        user_id=user.user_id,
        schedule_id=schedule.schedule_id,
        total_amount=total,
        booking_status=Booking.STATUS_CONFIRMED,
        contact_email=user.email,
        contact_phone=user.phone,
        hold_expires_at=None,
    )
    db.session.add(booking)
    db.session.flush()

    for seat in seats:
        seat.status = Seat.STATUS_BOOKED
        seat.current_booking_id = booking.booking_id
        db.session.add(
            BookingSeat(
                booking_id=booking.booking_id,
                seat_id=seat.seat_id,
                active_seat_id=seat.seat_id,
                is_active=True,
                price=schedule.seat_price(seat.seat_class),
            )
        )

    names = [("Demo Passenger", "1992-04-18", "MALE", "AADHAAR", "123456789012"),
             ("Ananya Passenger", "1995-11-02", "FEMALE", "PASSPORT", "M1234567")]
    for (full_name, dob, gender, id_type, id_number), seat in zip(names, seats):
        db.session.add(
            Passenger(
                booking_id=booking.booking_id,
                full_name=full_name,
                date_of_birth=date.fromisoformat(dob),
                gender=gender,
                identification_type=id_type,
                identification_number=id_number,
                seat_id=seat.seat_id,
            )
        )

    db.session.add(
        Payment(
            booking_id=booking.booking_id,
            transaction_reference="TNXSEED0001",
            amount=total,
            payment_method="CARD",
            payment_status=Payment.STATUS_SUCCESS,
            gateway_message="Seeded demo payment.",
            attempts=1,
            payment_time=utcnow(),
        )
    )
    db.session.add(
        Ticket(
            booking_id=booking.booking_id,
            ticket_number="TKT-0000000001",
            generated_at=utcnow(),
        )
    )
    db.session.commit()


def seed_database(days: int = 10) -> str:
    """Populate the database. Safe to run repeatedly."""
    try:
        airports = _seed_airports()
        users = _seed_users()
        flights = _seed_flights(airports)
        _seed_schedules(flights, days=days)
        _seed_demo_booking(users)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise
    return (
        f"Seeded {Airport.query.count()} airports, {Flight.query.count()} flights, "
        f"{FlightSchedule.query.count()} schedules, {Seat.query.count()} seats, "
        f"{User.query.count()} users."
    )

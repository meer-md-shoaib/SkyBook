"""Administrator dashboard and management pages."""
from datetime import datetime

from flask import (
    Blueprint, abort, flash, redirect, render_template, request, url_for,
)
from flask_login import login_required
from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.extensions import db
from app.models import (
    Airport, Booking, Cancellation, Flight, FlightSchedule, Payment, Seat,
)
from app.repositories.booking_repository import BookingRepository
from app.repositories.flight_repository import FlightRepository
from app.repositories.user_repository import UserRepository
from app.services.booking_service import BookingService
from app.services.seat_service import SeatLayoutError, SeatService
from app.utils.decorators import admin_required
from app.utils.helpers import utcnow

admin_bp = Blueprint("admin", __name__)

flight_repo = FlightRepository()
booking_repo = BookingRepository()


def _parse_datetime(value: str):
    if not value:
        return None
    for fmt in ("%Y-%m-%dT%H:%M", "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M:%S"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _fmt_input(value: datetime | None) -> str:
    return value.strftime("%Y-%m-%dT%H:%M") if value else ""


@admin_bp.route("/")
@login_required
@admin_required
def dashboard():
    from flask import current_app

    try:
        BookingService().expire_stale_holds()
    except Exception:  # pragma: no cover
        current_app.logger.warning("Failed to expire stale holds on admin dashboard", exc_info=True)

    stats = booking_repo.stats()
    now = utcnow()
    upcoming = FlightSchedule.query.filter(
        FlightSchedule.departure_time >= now,
        FlightSchedule.status == FlightSchedule.STATUS_SCHEDULED,
    ).count()
    stats.update(
        {
            "flights": Flight.query.count(),
            "schedules": FlightSchedule.query.count(),
            "upcoming": upcoming,
            "passengers": UserRepository.count_passengers(),
            "airports": Airport.query.count(),
            "cancellations": Cancellation.query.count(),
            "pending": Booking.query.filter_by(booking_status="PENDING").count(),
            "seats_booked": Seat.query.filter_by(status="BOOKED").count(),
        }
    )
    recent_bookings = booking_repo.recent(8)
    recent_cancellations = (
        Cancellation.query.order_by(Cancellation.cancellation_date.desc()).limit(5).all()
    )
    top_routes = (
        db.session.query(
            Airport.city, func.count(FlightSchedule.schedule_id).label("total")
        )
        .join(Flight, Flight.source_airport_id == Airport.airport_id)
        .join(FlightSchedule, FlightSchedule.flight_id == Flight.flight_id)
        .group_by(Airport.city)
        .order_by(func.count(FlightSchedule.schedule_id).desc())
        .limit(5)
        .all()
    )
    return render_template(
        "admin/dashboard.html",
        stats=stats,
        recent_bookings=recent_bookings,
        recent_cancellations=recent_cancellations,
        top_routes=top_routes,
    )


# ----------------------------------------------------------------------
# Flights
# ----------------------------------------------------------------------
@admin_bp.route("/flights")
@login_required
@admin_required
def flights():
    all_flights = (
        Flight.query.options(
            joinedload(Flight.source_airport),
            joinedload(Flight.destination_airport),
        )
        .order_by(Flight.flight_number.asc())
        .all()
    )
    return render_template(
        "admin/flights.html",
        flights=all_flights,
        airports=flight_repo.list_airports(),
    )


@admin_bp.route("/flights/new", methods=["POST"])
@login_required
@admin_required
def create_flight():
    flight_number = (request.form.get("flight_number") or "").strip().upper()
    airline = (request.form.get("airline_name") or "").strip()
    try:
        source_id = int(request.form.get("source_airport_id"))
        dest_id = int(request.form.get("destination_airport_id"))
    except (TypeError, ValueError):
        flash("Select valid source and destination airports.", "danger")
        return redirect(url_for("admin.flights"))

    errors = []
    if not flight_number or len(flight_number) > 10:
        errors.append("Flight number is required (max 10 characters).")
    if not airline:
        errors.append("Airline name is required.")
    if source_id == dest_id:
        errors.append("Source and destination airports must differ.")
    if not db.session.get(Airport, source_id) or not db.session.get(Airport, dest_id):
        errors.append("Selected airport does not exist.")
    if Flight.query.filter_by(flight_number=flight_number).first():
        errors.append(f"Flight {flight_number} already exists.")

    if errors:
        for error in errors:
            flash(error, "danger")
        return redirect(url_for("admin.flights"))

    db.session.add(
        Flight(
            flight_number=flight_number,
            airline_name=airline,
            source_airport_id=source_id,
            destination_airport_id=dest_id,
            aircraft_type=(request.form.get("aircraft_type") or "Airbus A320").strip(),
            is_active=True,
        )
    )
    db.session.commit()
    flash(f"Flight {flight_number} added.", "success")
    return redirect(url_for("admin.flights"))


@admin_bp.route("/flights/<int:flight_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_flight(flight_id: int):
    flight = db.session.get(Flight, flight_id)
    if not flight:
        abort(404)
    airline = (request.form.get("airline_name") or "").strip()
    if airline:
        flight.airline_name = airline
    aircraft = (request.form.get("aircraft_type") or "").strip()
    if aircraft:
        flight.aircraft_type = aircraft
    try:
        source_id = int(request.form.get("source_airport_id") or flight.source_airport_id)
        dest_id = int(request.form.get("destination_airport_id") or flight.destination_airport_id)
    except (TypeError, ValueError):
        flash("Invalid airport selection.", "danger")
        return redirect(url_for("admin.flights"))
    if source_id == dest_id:
        flash("Source and destination airports must differ.", "danger")
        return redirect(url_for("admin.flights"))
    flight.source_airport_id = source_id
    flight.destination_airport_id = dest_id
    db.session.commit()
    flash(f"Flight {flight.flight_number} updated.", "success")
    return redirect(url_for("admin.flights"))


@admin_bp.route("/flights/<int:flight_id>/toggle", methods=["POST"])
@login_required
@admin_required
def toggle_flight(flight_id: int):
    flight = db.session.get(Flight, flight_id)
    if not flight:
        abort(404)
    flight.is_active = not flight.is_active
    db.session.commit()
    state = "activated" if flight.is_active else "deactivated"
    flash(f"Flight {flight.flight_number} {state}.", "success")
    return redirect(url_for("admin.flights"))


# ----------------------------------------------------------------------
# Schedules
# ----------------------------------------------------------------------
@admin_bp.route("/schedules")
@login_required
@admin_required
def schedules():
    rows = (
        FlightSchedule.query.options(
            joinedload(FlightSchedule.flight).joinedload(Flight.source_airport),
            joinedload(FlightSchedule.flight).joinedload(Flight.destination_airport),
        )
        .order_by(FlightSchedule.departure_time.asc())
        .all()
    )
    return render_template(
        "admin/schedules.html",
        schedules=rows,
        flights=flight_repo.list_flights(),
    )


@admin_bp.route("/schedules/new", methods=["POST"])
@login_required
@admin_required
def create_schedule():
    try:
        flight_id = int(request.form.get("flight_id"))
        departure = _parse_datetime(request.form.get("departure_time"))
        arrival = _parse_datetime(request.form.get("arrival_time"))
        base_fare = float(request.form.get("base_fare"))
    except (TypeError, ValueError):
        flash("Enter a valid flight, departure, arrival and fare.", "danger")
        return redirect(url_for("admin.schedules"))

    flight = db.session.get(Flight, flight_id)
    if not flight:
        flash("Selected flight does not exist.", "danger")
        return redirect(url_for("admin.schedules"))
    if not departure or not arrival:
        flash("Departure and arrival times are required.", "danger")
        return redirect(url_for("admin.schedules"))
    if arrival <= departure:
        flash("Arrival must be after departure.", "danger")
        return redirect(url_for("admin.schedules"))
    if base_fare <= 0:
        flash("Fare must be greater than zero.", "danger")
        return redirect(url_for("admin.schedules"))

    schedule = FlightSchedule(
        flight_id=flight.flight_id,
        departure_time=departure,
        arrival_time=arrival,
        base_fare=base_fare,
        status=FlightSchedule.STATUS_SCHEDULED,
    )
    db.session.add(schedule)
    db.session.flush()

    try:
        business_rows = int(request.form.get("business_rows") or 3)
        economy_rows = int(request.form.get("economy_rows") or 20)
    except (TypeError, ValueError):
        business_rows, economy_rows = 3, 20
    created = SeatService.generate(schedule, business_rows, economy_rows)
    db.session.commit()
    flash(
        f"Schedule added for {flight.flight_number} with {created} seats.", "success"
    )
    return redirect(url_for("admin.schedules"))


@admin_bp.route("/schedules/<int:schedule_id>/edit", methods=["POST"])
@login_required
@admin_required
def edit_schedule(schedule_id: int):
    schedule = db.session.get(FlightSchedule, schedule_id)
    if not schedule:
        abort(404)

    departure = _parse_datetime(request.form.get("departure_time"))
    arrival = _parse_datetime(request.form.get("arrival_time"))
    status = request.form.get("status", schedule.status)
    try:
        base_fare = float(request.form.get("base_fare"))
    except (TypeError, ValueError):
        flash("Fare must be a number.", "danger")
        return redirect(url_for("admin.schedules"))

    if not departure or not arrival or arrival <= departure:
        flash("Arrival must be after departure.", "danger")
        return redirect(url_for("admin.schedules"))
    if base_fare <= 0:
        flash("Fare must be greater than zero.", "danger")
        return redirect(url_for("admin.schedules"))
    if status not in ("SCHEDULED", "DEPARTED", "CANCELLED", "COMPLETED"):
        flash("Invalid schedule status.", "danger")
        return redirect(url_for("admin.schedules"))

    schedule.departure_time = departure
    schedule.arrival_time = arrival
    schedule.base_fare = base_fare
    schedule.status = status
    db.session.commit()
    flash("Schedule updated.", "success")
    return redirect(url_for("admin.schedules"))


@admin_bp.route("/schedules/<int:schedule_id>/seats")
@login_required
@admin_required
def schedule_seats(schedule_id: int):
    schedule = db.session.get(FlightSchedule, schedule_id)
    if not schedule:
        abort(404)
    seats = FlightRepository.get_schedule_seats(schedule_id)
    return render_template(
        "admin/seat_config.html",
        schedule=schedule,
        seats=seats,
        counts=SeatService.counts(schedule_id),
    )


@admin_bp.route("/schedules/<int:schedule_id>/seats/regenerate", methods=["POST"])
@login_required
@admin_required
def regenerate_seats(schedule_id: int):
    schedule = db.session.get(FlightSchedule, schedule_id)
    if not schedule:
        abort(404)
    try:
        business_rows = int(request.form.get("business_rows") or 3)
        economy_rows = int(request.form.get("economy_rows") or 20)
    except (TypeError, ValueError):
        flash("Row counts must be numbers.", "danger")
        return redirect(url_for("admin.schedule_seats", schedule_id=schedule_id))
    try:
        created = SeatService.generate(schedule, business_rows, economy_rows, replace=True)
        db.session.commit()
    except SeatLayoutError as exc:
        db.session.rollback()
        flash(str(exc), "danger")
        return redirect(url_for("admin.schedule_seats", schedule_id=schedule_id))
    flash(f"Seat map regenerated ({created} seats).", "success")
    return redirect(url_for("admin.schedule_seats", schedule_id=schedule_id))


# ----------------------------------------------------------------------
# Reservations / passengers / payments / cancellations
# ----------------------------------------------------------------------
@admin_bp.route("/bookings")
@login_required
@admin_required
def bookings():
    status = request.args.get("status", "").upper()
    search = (request.args.get("q") or "").strip()
    query = Booking.query.options(
        joinedload(Booking.user),
        joinedload(Booking.schedule).joinedload(FlightSchedule.flight),
    )
    if status:
        query = query.filter(Booking.booking_status == status)
    if search:
        safe_search = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        query = query.filter(Booking.booking_reference.ilike(f"%{safe_search}%", escape="\\"))
    rows = query.order_by(Booking.created_at.desc()).limit(200).all()
    return render_template(
        "admin/bookings.html",
        bookings=rows,
        status=status,
        search=search,
        counts={
            s: Booking.query.filter_by(booking_status=s).count()
            for s in ("PENDING", "CONFIRMED", "CANCELLED", "EXPIRED")
        },
    )


@admin_bp.route("/bookings/<int:booking_id>")
@login_required
@admin_required
def booking_detail(booking_id: int):
    booking = db.session.get(Booking, booking_id)
    if not booking:
        abort(404)
    return render_template("admin/booking_detail.html", booking=booking)


@admin_bp.route("/passengers")
@login_required
@admin_required
def passengers():
    users = UserRepository.list_passengers()
    return render_template("admin/passengers.html", users=users)


@admin_bp.route("/payments")
@login_required
@admin_required
def payments():
    rows = Payment.query.order_by(Payment.created_at.desc()).limit(200).all()
    totals = {
        "success": Payment.query.filter_by(payment_status="SUCCESS").count(),
        "failed": Payment.query.filter_by(payment_status="FAILED").count(),
        "refunded": Payment.query.filter_by(payment_status="REFUNDED").count(),
        "amount": float(
            db.session.query(func.coalesce(func.sum(Payment.amount), 0))
            .filter(Payment.payment_status == "SUCCESS")
            .scalar()
            or 0
        ),
    }
    return render_template("admin/payments.html", payments=rows, totals=totals)


@admin_bp.route("/cancellations")
@login_required
@admin_required
def cancellations():
    rows = (
        Cancellation.query.order_by(Cancellation.cancellation_date.desc()).limit(100).all()
    )
    return render_template("admin/cancellations.html", cancellations=rows)

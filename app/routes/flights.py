"""Flight search, results, details and seat selection."""
from flask import (
    Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for,
)
from flask_login import current_user, login_required

from app.models import Seat
from app.services.booking_service import BookingError, BookingService
from app.services.flight_service import FlightService

flights_bp = Blueprint("flights", __name__)

flight_service = FlightService()
booking_service = BookingService()


@flights_bp.route("/search", methods=["GET", "POST"])
def search():
    """Landing-page search form -> results page (POST redirected to GET)."""
    if request.method == "POST":
        args = {
            "source": request.form.get("source", ""),
            "destination": request.form.get("destination", ""),
            "date": request.form.get("travel_date", ""),
            "passengers": request.form.get("passengers", "1"),
        }
        return redirect(url_for("flights.results", **args))
    return redirect(url_for("main.index"))


@flights_bp.route("/results")
def results():
    from flask import current_app

    source = request.args.get("source", "")
    destination = request.args.get("destination", "")
    travel_date = request.args.get("date", "")
    passengers = request.args.get("passengers", "1")

    try:
        booking_service.expire_stale_holds()
    except Exception:  # pragma: no cover
        current_app.logger.warning("Failed to expire stale holds before search", exc_info=True)

    outcome = flight_service.search(
        source=source,
        destination=destination,
        travel_date=travel_date,
        passengers=passengers,
        airline=request.args.get("airline") or None,
        max_price=request.args.get("max_price") or None,
        departure_window=request.args.get("departure_window") or None,
    )

    return render_template(
        "flights.html",
        flights=outcome["flights"],
        errors=outcome["errors"],
        criteria=outcome["criteria"],
        airlines=flight_service.airlines(),
        cities=flight_service.cities(),
    )


@flights_bp.route("/<int:schedule_id>")
def details(schedule_id: int):
    schedule = flight_service.get_schedule(schedule_id)
    if not schedule:
        abort(404)
    return render_template("flight_details.html", schedule=schedule)


@flights_bp.route("/<int:schedule_id>/seats")
@login_required
def seats(schedule_id: int):
    schedule = flight_service.get_schedule(schedule_id)
    if not schedule:
        abort(404)

    # Refresh availability before rendering (expired holds become free again).
    try:
        booking_service.expire_stale_holds()
    except Exception:  # pragma: no cover
        current_app.logger.warning("Failed to expire stale holds in seat map", exc_info=True)

    seat_data = flight_service.seat_map(schedule_id)
    passengers = request.args.get("passengers", "1")
    try:
        passengers = max(1, min(int(passengers), 6))
    except (TypeError, ValueError):
        passengers = 1

    return render_template(
        "seats.html",
        schedule=schedule,
        rows=seat_data["rows"],
        counts=seat_data["counts"],
        passengers=passengers,
        hold_minutes=current_app_config("SEAT_HOLD_MINUTES", 10),
    )


@flights_bp.route("/<int:schedule_id>/seats/hold", methods=["POST"])
@login_required
def hold_seats(schedule_id: int):
    seat_ids = request.form.getlist("seat_ids")
    if not seat_ids:
        flash("Select at least one seat to continue.", "warning")
        return redirect(url_for("flights.seats", schedule_id=schedule_id))

    try:
        booking = booking_service.create_pending_booking(
            user=current_user,
            schedule_id=schedule_id,
            seat_ids=[int(s) for s in seat_ids],
            contact_email=current_user.email,
            contact_phone=current_user.phone,
        )
    except BookingError as exc:
        flash(str(exc), "danger")
        return redirect(url_for("flights.seats", schedule_id=schedule_id))
    except Exception as exc:  # pragma: no cover
        from flask import current_app
        current_app.logger.exception("Failed to hold seats: %s", exc)
        flash("We could not hold those seats. Please try again.", "danger")
        return redirect(url_for("flights.seats", schedule_id=schedule_id))

    flash(
        f"Seats held for {booking.seat_numbers}. Complete passenger details within "
        f"{current_app_config('SEAT_HOLD_MINUTES', 10)} minutes.",
        "success",
    )
    return redirect(url_for("bookings.passenger_details", booking_id=booking.booking_id))


@flights_bp.route("/<int:schedule_id>/availability")
def availability(schedule_id: int):
    """JSON availability endpoint used by the seat map for live refreshes.

    Returns:
        JSON object with:
            counts (dict): Total, available, held, and booked seat tallies.
            seats (list[dict]): Array of seat objects with 'id', 'number', and 'status'.
    """
    data = flight_service.seat_map(schedule_id)
    if not data:
        return jsonify({"error": "not found"}), 404
    payload = {
        "counts": data["counts"],
        "seats": [],
    }
    for row in data["rows"]:
        for seat in row["columns"]:
            if seat:
                payload["seats"].append(
                    {"id": seat["id"], "number": seat["number"], "status": seat["status"]}
                )
    return jsonify(payload)


def current_app_config(key: str, default=None):
    from flask import current_app

    return current_app.config.get(key, default)

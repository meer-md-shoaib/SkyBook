"""Passenger booking pages: details, summary, history and cancellation."""
from flask import (
    Blueprint, abort, flash, redirect, render_template, request, url_for,
)
from flask_login import current_user, login_required

from app.services.booking_service import BookingError, BookingService
from app.services.cancellation_service import CancellationError, CancellationService
from app.utils.validators import GENDERS, ID_TYPE_LABELS, ID_TYPES

bookings_bp = Blueprint("bookings", __name__)

booking_service = BookingService()
cancellation_service = CancellationService()


def _owned_or_404(booking_id: int):
    booking_service.expire_stale_holds()
    booking = booking_service.get_owned_booking(booking_id, current_user)
    if not booking:
        abort(404)
    return booking


@bookings_bp.route("/")
@login_required
def my_bookings():
    """Display all bookings associated with the currently signed-in user."""
    booking_service.expire_stale_holds()
    bookings = booking_service.repo.list_for_user(current_user.user_id)
    return render_template("my_bookings.html", bookings=bookings)


@bookings_bp.route("/<int:booking_id>")
@login_required
def details(booking_id: int):
    """View details, seat information, and cancellation eligibility for a booking."""
    booking = _owned_or_404(booking_id)
    eligible, reason = cancellation_service.eligibility(booking)
    return render_template(
        "booking_details.html",
        booking=booking,
        eligible=eligible,
        eligibility_reason=reason,
        quote=cancellation_service.refund_quote(booking) if eligible else None,
    )


@bookings_bp.route("/<int:booking_id>/passengers", methods=["GET", "POST"])
@login_required
def passenger_details(booking_id: int):
    """Collect and validate identification details for each held seat."""
    booking = _owned_or_404(booking_id)
    if booking.booking_status != "PENDING":
        return redirect(url_for("bookings.details", booking_id=booking.booking_id))

    if booking.is_hold_expired:
        booking_service.expire_stale_holds()
        flash("Your seat hold expired. Please select seats again.", "warning")
        return redirect(url_for("flights.seats", schedule_id=booking.schedule_id))

    seat_count = len(booking.active_seats)

    if request.method == "POST":
        payloads = []
        for index in range(seat_count):
            payloads.append(
                {
                    "full_name": request.form.get(f"full_name_{index}", ""),
                    "date_of_birth": request.form.get(f"date_of_birth_{index}", ""),
                    "gender": request.form.get(f"gender_{index}", ""),
                    "identification_type": request.form.get(f"identification_type_{index}", ""),
                    "identification_number": request.form.get(
                        f"identification_number_{index}", ""
                    ),
                }
            )
        errors = booking_service.save_passengers(booking, payloads)
        if errors:
            for error in errors:
                flash(error, "danger")
            return render_template(
                "passenger_details.html",
                booking=booking,
                seat_count=seat_count,
                submitted=payloads,
                id_types=ID_TYPES,
                id_labels=ID_TYPE_LABELS,
                genders=GENDERS,
                hold_seconds=booking.hold_seconds_remaining,
            )
        flash("Passenger details saved. Review your booking and continue to payment.", "success")
        return redirect(url_for("bookings.summary", booking_id=booking.booking_id))

    existing = [
        {
            "full_name": p.full_name,
            "date_of_birth": p.date_of_birth.isoformat() if p.date_of_birth else "",
            "gender": p.gender,
            "identification_type": p.identification_type,
            "identification_number": p.identification_number,
        }
        for p in booking.passengers
    ]
    return render_template(
        "passenger_details.html",
        booking=booking,
        seat_count=seat_count,
        submitted=existing,
        id_types=ID_TYPES,
        id_labels=ID_TYPE_LABELS,
        genders=GENDERS,
        hold_seconds=booking.hold_seconds_remaining,
    )


@bookings_bp.route("/<int:booking_id>/summary")
@login_required
def summary(booking_id: int):
    """Review booking breakdown, flight times, and fare before paying."""
    booking = _owned_or_404(booking_id)
    if len(booking.passengers) != len(booking.active_seats):
        flash("Please complete passenger details before reviewing the booking.", "warning")
        return redirect(url_for("bookings.passenger_details", booking_id=booking.booking_id))
    return render_template("booking_summary.html", booking=booking)


@bookings_bp.route("/<int:booking_id>/confirmation")
@login_required
def confirmation(booking_id: int):
    """Booking success screen with e-ticket download link."""
    booking = _owned_or_404(booking_id)
    if booking.booking_status != "CONFIRMED":
        flash("This booking is not confirmed yet.", "warning")
        return redirect(url_for("bookings.details", booking_id=booking.booking_id))
    return render_template("confirmation.html", booking=booking)


@bookings_bp.route("/<int:booking_id>/cancel", methods=["GET", "POST"])
@login_required
def cancel(booking_id: int):
    """Quote cancellation refund and release held/booked seats upon confirmation."""
    booking = _owned_or_404(booking_id)
    eligible, reason = cancellation_service.eligibility(booking)
    quote = cancellation_service.refund_quote(booking)

    if request.method == "POST":
        if not eligible:
            flash(reason, "danger")
            return redirect(url_for("bookings.details", booking_id=booking.booking_id))
        confirmation_text = request.form.get("confirm", "")
        if confirmation_text.lower() not in ("yes", "on", "true", "1"):
            flash("Please confirm the cancellation to proceed.", "warning")
            return render_template(
                "cancellation.html", booking=booking, eligible=eligible,
                eligibility_reason=reason, quote=quote,
            )
        try:
            cancellation = cancellation_service.cancel(
                booking, request.form.get("reason", "Cancelled by passenger")
            )
        except CancellationError as exc:
            flash(str(exc), "danger")
            return redirect(url_for("bookings.details", booking_id=booking.booking_id))
        flash(
            "Booking cancelled. Seats released and a refund of "
            f"₹{float(cancellation.refund_amount):,.2f} recorded.",
            "success",
        )
        return redirect(url_for("bookings.details", booking_id=booking.booking_id))

    return render_template(
        "cancellation.html",
        booking=booking,
        eligible=eligible,
        eligibility_reason=reason,
        quote=quote,
    )

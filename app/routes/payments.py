"""Simulated payment checkout, retry and gateway callback."""
from flask import Blueprint, abort, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app.extensions import csrf
from app.models import Payment
from app.services.booking_service import BookingService
from app.services.payment_service import PaymentService

payments_bp = Blueprint("payments", __name__)

booking_service = BookingService()
payment_service = PaymentService()


def _get_booking(booking_id: int):
    booking_service.expire_stale_holds()
    booking = booking_service.repo.get_by_id(booking_id)
    if not booking or booking.user_id != current_user.user_id:
        abort(404)
    return booking


@payments_bp.route("/<int:booking_id>")
@login_required
def checkout(booking_id: int):
    """Render simulated payment checkout screen with card/UPI and outcome choices."""
    booking = _get_booking(booking_id)
    if booking.booking_status == "CONFIRMED":
        return redirect(url_for("bookings.confirmation", booking_id=booking.booking_id))
    if booking.booking_status == "CANCELLED":
        flash("That booking was cancelled.", "danger")
        return redirect(url_for("bookings.my_bookings"))
    if booking.booking_status == "EXPIRED" or booking.is_hold_expired:
        flash("Your seat hold expired before payment. Please book again.", "warning")
        return redirect(url_for("bookings.my_bookings"))
    if len(booking.passengers) != len(booking.active_seats):
        flash("Please complete passenger details before paying.", "warning")
        return redirect(url_for("bookings.passenger_details", booking_id=booking.booking_id))

    return render_template(
        "payment.html",
        booking=booking,
        payment=booking.payment,
        hold_seconds=booking.hold_seconds_remaining,
    )


@payments_bp.route("/<int:booking_id>/pay", methods=["POST"])
@login_required
def pay(booking_id: int):
    """Execute simulated charge; confirm booking on success or retain pending on failure."""
    outcome = request.form.get("outcome", "success")
    method = request.form.get("payment_method", "CARD")
    simulate_failure = outcome == "failure"

    result = payment_service.process_payment(
        booking_id=booking_id,
        user=current_user,
        method=method,
        simulate_failure=simulate_failure,
    )

    if result.success:
        flash("Payment successful — your booking is confirmed and the e-ticket is ready.", "success")
        return redirect(url_for("bookings.confirmation", booking_id=booking_id))

    flash(result.message, "danger")
    return redirect(url_for("payments.checkout", booking_id=booking_id))


@payments_bp.route("/<int:booking_id>/retry", methods=["POST"])
@login_required
def retry(booking_id: int):
    """Retry payment while the original seat hold is still valid."""
    return pay(booking_id)


@payments_bp.route("/callback", methods=["POST"])
@csrf.exempt
def gateway_callback():
    """Idempotent webhook endpoint for a (simulated) payment provider.

    Repeated callbacks never confirm twice: an existing SUCCESS payment is
    returned as-is.
    """
    data = request.get_json(silent=True) or request.form
    reference = data.get("transaction_reference")
    if not reference:
        return jsonify({"ok": False, "error": "missing transaction_reference"}), 400

    payment = Payment.query.filter_by(transaction_reference=reference).first()
    if not payment:
        return jsonify({"ok": False, "error": "unknown transaction"}), 404
    if payment.payment_status == Payment.STATUS_SUCCESS:
        return jsonify({"ok": True, "status": "SUCCESS", "duplicate": True})
    return jsonify(
        {
            "ok": True,
            "status": payment.payment_status,
            "booking": payment.booking.booking_reference,
        }
    )

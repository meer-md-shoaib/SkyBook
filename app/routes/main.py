"""Landing page and lightweight status endpoints."""
from flask import Blueprint, jsonify, render_template

from app.repositories.flight_repository import FlightRepository
from app.services.booking_service import BookingService
from app.services.flight_service import FlightService

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def index():
    service = FlightService()
    # Opportunistically release expired holds so the landing page is accurate.
    try:
        BookingService().expire_stale_holds()
    except Exception:  # pragma: no cover - never block the landing page
        from flask import current_app
        current_app.logger.warning("Failed to expire stale holds on index", exc_info=True)
    return render_template(
        "index.html",
        cities=service.cities(),
        upcoming=service.schedules()[:3],
        airlines=service.airlines(),
        airports=FlightRepository.list_airports()[:6],
    )


@main_bp.route("/services")
def services():
    """Dedicated travel services and amenities showcase page."""
    return render_template("services.html")


@main_bp.route("/contact", methods=["GET", "POST"])
def contact():
    """Dedicated passenger support and contact page."""
    from flask import flash, request
    if request.method == "POST":
        name = (request.form.get("name") or "").strip()
        email = (request.form.get("email") or "").strip()
        message = (request.form.get("message") or "").strip()
        if name and email and message:
            flash(
                "Thank you for reaching out! Our support team (shoaibmeermd@gmail.com) "
                "has received your message and will get back to you promptly.",
                "success",
            )
        else:
            flash("Please provide your name, valid email address, and inquiry message.", "warning")
    return render_template("contact.html")


@main_bp.route("/health")
def health():
    return jsonify({"status": "ok", "app": "SkyBook"})

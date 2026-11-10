"""Electronic ticket download."""
import os

from flask import Blueprint, abort, flash, redirect, send_file, url_for
from flask_login import current_user, login_required

from app.extensions import db
from app.services.ticket_service import TicketService

tickets_bp = Blueprint("tickets", __name__)

ticket_service = TicketService()


@tickets_bp.route("/<int:booking_id>/download")
@login_required
def download(booking_id: int):
    from app.models import Booking

    booking = db.session.get(Booking, booking_id)
    if not booking:
        abort(404)
    # Owners and administrators only.
    if booking.user_id != current_user.user_id and not getattr(current_user, "is_admin", False):
        abort(403)
    if booking.booking_status != "CONFIRMED":
        flash("Tickets are only available for confirmed bookings.", "warning")
        return redirect(url_for("bookings.details", booking_id=booking_id))

    path = ticket_service.file_for(booking)
    if not path:
        ticket_service.generate_for_booking(booking)
        db.session.commit()
        path = ticket_service.file_for(booking)

    if not path:
        flash("We could not generate the ticket. Please try again.", "danger")
        return redirect(url_for("bookings.details", booking_id=booking_id))

    return send_file(
        path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=os.path.basename(path),
    )

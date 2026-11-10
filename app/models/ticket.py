"""Electronic ticket metadata (PDF lives on disk / in generated_tickets)."""
import secrets
import string
from datetime import datetime

from app.extensions import db
from app.utils.helpers import utcnow


def generate_ticket_number() -> str:
    digits = "".join(secrets.choice(string.digits) for _ in range(10))
    return f"TKT-{digits}"


class Ticket(db.Model):
    __tablename__ = "tickets"

    ticket_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(
        db.Integer, db.ForeignKey("bookings.booking_id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True,
    )
    ticket_number = db.Column(
        db.String(20), nullable=False, unique=True, index=True,
        default=generate_ticket_number,
    )
    generated_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    file_path = db.Column(db.String(255), nullable=True)

    booking = db.relationship("Booking", back_populates="ticket")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Ticket {self.ticket_number}>"

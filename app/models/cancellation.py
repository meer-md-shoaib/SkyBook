"""Cancellation and refund record."""
from datetime import datetime

from app.extensions import db
from app.utils.helpers import utcnow


class Cancellation(db.Model):
    __tablename__ = "cancellations"

    STATUS_PENDING = "PENDING"
    STATUS_PROCESSED = "PROCESSED"
    STATUS_REJECTED = "REJECTED"

    cancellation_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(
        db.Integer, db.ForeignKey("bookings.booking_id", ondelete="CASCADE"),
        nullable=False, unique=True, index=True,
    )
    cancellation_reason = db.Column(db.String(255), nullable=True)
    refund_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    cancellation_date = db.Column(db.DateTime, nullable=False, default=utcnow)
    refund_status = db.Column(
        db.Enum("PENDING", "PROCESSED", "REJECTED", name="refund_status"),
        nullable=False, default=STATUS_PENDING, index=True,
    )
    processed_at = db.Column(db.DateTime, nullable=True)

    booking = db.relationship("Booking", back_populates="cancellation")

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Cancellation booking={self.booking_id} refund={self.refund_amount}>"

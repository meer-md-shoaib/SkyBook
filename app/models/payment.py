"""Payment transaction record (simulated gateway)."""
from datetime import datetime

from app.extensions import db
from app.utils.helpers import utcnow


class Payment(db.Model):
    __tablename__ = "payments"

    STATUS_PENDING = "PENDING"
    STATUS_SUCCESS = "SUCCESS"
    STATUS_FAILED = "FAILED"
    STATUS_REFUNDED = "REFUNDED"

    payment_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(
        db.Integer, db.ForeignKey("bookings.booking_id", ondelete="CASCADE"),
        nullable=False, index=True, unique=True,
    )
    transaction_reference = db.Column(
        db.String(40), nullable=False, unique=True, index=True
    )
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default="INR")
    payment_method = db.Column(db.String(30), nullable=False, default="CARD")
    payment_status = db.Column(
        db.Enum("PENDING", "SUCCESS", "FAILED", "REFUNDED", name="payment_status"),
        nullable=False, default=STATUS_PENDING, index=True,
    )
    gateway_message = db.Column(db.String(255), nullable=True)
    attempts = db.Column(db.Integer, nullable=False, default=0)
    payment_time = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )

    booking = db.relationship("Booking", back_populates="payment")

    @property
    def status_label(self) -> str:
        return self.payment_status.title()

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Payment {self.transaction_reference} {self.payment_status}>"

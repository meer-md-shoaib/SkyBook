"""Booking and the booking-seat join table."""
import secrets
import string
from datetime import datetime

from app.extensions import db
from app.utils.helpers import utcnow

ALPHABET = string.ascii_uppercase + string.digits


def generate_booking_reference() -> str:
    """Human friendly, unique-enough reference such as SB7K3Q2M."""
    return "SB" + "".join(secrets.choice(ALPHABET) for _ in range(6))


class Booking(db.Model):
    __tablename__ = "bookings"
    __table_args__ = (
        db.Index("ix_booking_user_status", "user_id", "booking_status"),
    )

    STATUS_PENDING = "PENDING"
    STATUS_CONFIRMED = "CONFIRMED"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_EXPIRED = "EXPIRED"

    booking_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_reference = db.Column(
        db.String(12), nullable=False, unique=True, index=True,
        default=generate_booking_reference,
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    schedule_id = db.Column(
        db.Integer, db.ForeignKey("flight_schedules.schedule_id", ondelete="RESTRICT"),
        nullable=False, index=True,
    )
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    booking_status = db.Column(
        db.Enum("PENDING", "CONFIRMED", "CANCELLED", "EXPIRED", name="booking_status"),
        nullable=False, default=STATUS_PENDING, index=True,
    )
    contact_email = db.Column(db.String(120), nullable=True)
    contact_phone = db.Column(db.String(20), nullable=True)
    hold_expires_at = db.Column(db.DateTime, nullable=True, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=utcnow, onupdate=utcnow
    )

    user = db.relationship("User", back_populates="bookings")
    schedule = db.relationship("FlightSchedule")
    passengers = db.relationship(
        "Passenger", back_populates="booking", cascade="all, delete-orphan", lazy="selectin"
    )
    seat_links = db.relationship(
        "BookingSeat", back_populates="booking", cascade="all, delete-orphan", lazy="selectin"
    )
    payment = db.relationship(
        "Payment", back_populates="booking", uselist=False, cascade="all, delete-orphan"
    )
    ticket = db.relationship(
        "Ticket", back_populates="booking", uselist=False, cascade="all, delete-orphan"
    )
    cancellation = db.relationship(
        "Cancellation", back_populates="booking", uselist=False, cascade="all, delete-orphan"
    )

    # ---- helpers ----------------------------------------------------------
    @property
    def active_seats(self):
        return [link.seat for link in self.seat_links if link.is_active and link.seat]

    @property
    def seat_numbers(self) -> str:
        return ", ".join(sorted(seat.seat_number for seat in self.active_seats))

    @property
    def passenger_count(self) -> int:
        return len(self.passengers)

    @property
    def is_hold_expired(self) -> bool:
        if self.booking_status != self.STATUS_PENDING or not self.hold_expires_at:
            return False
        return utcnow() > self.hold_expires_at

    @property
    def hold_seconds_remaining(self) -> int:
        if self.booking_status != self.STATUS_PENDING or not self.hold_expires_at:
            return 0
        delta = self.hold_expires_at - utcnow()
        return max(0, int(delta.total_seconds()))

    @property
    def can_cancel(self) -> bool:
        return (
            self.booking_status == self.STATUS_CONFIRMED
            and self.schedule is not None
            and self.schedule.departure_time > utcnow()
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Booking {self.booking_reference} {self.booking_status}>"


class BookingSeat(db.Model):
    """Join row between a booking and the seats it holds.

    ``active_seat_id`` is a nullable copy of ``seat_id`` protected by a UNIQUE
    index. Active rows therefore guarantee one booking per seat at the database
    level, while released rows (NULL) keep their history.
    """

    __tablename__ = "booking_seats"
    __table_args__ = (
        db.UniqueConstraint("active_seat_id", name="uq_active_seat"),
        db.UniqueConstraint("booking_id", "seat_id", name="uq_booking_seat"),
    )

    booking_seat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(
        db.Integer, db.ForeignKey("bookings.booking_id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    seat_id = db.Column(
        db.Integer, db.ForeignKey("seats.seat_id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    active_seat_id = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    price = db.Column(db.Numeric(10, 2), nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    booking = db.relationship("Booking", back_populates="seat_links")
    seat = db.relationship("Seat")

    def release(self) -> None:
        self.is_active = False
        self.active_seat_id = None

    def __repr__(self) -> str:  # pragma: no cover
        return f"<BookingSeat booking={self.booking_id} seat={self.seat_id}>"

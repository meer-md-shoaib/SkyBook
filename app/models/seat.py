"""Seat inventory for a specific flight schedule."""
from app.extensions import db


class Seat(db.Model):
    __tablename__ = "seats"
    __table_args__ = (
        db.UniqueConstraint("schedule_id", "seat_number", name="uq_seat_schedule_number"),
        db.Index("ix_seat_schedule_status", "schedule_id", "status"),
    )

    STATUS_AVAILABLE = "AVAILABLE"
    STATUS_HELD = "HELD"
    STATUS_BOOKED = "BOOKED"

    seat_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    schedule_id = db.Column(
        db.Integer, db.ForeignKey("flight_schedules.schedule_id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    seat_number = db.Column(db.String(5), nullable=False)
    seat_class = db.Column(
        db.Enum("ECONOMY", "BUSINESS", "FIRST", name="seat_class"),
        nullable=False, default="ECONOMY", index=True,
    )
    seat_row = db.Column(db.Integer, nullable=False, default=1)
    seat_column = db.Column(db.String(1), nullable=False, default="A")
    status = db.Column(
        db.Enum("AVAILABLE", "HELD", "BOOKED", name="seat_status"),
        nullable=False, default=STATUS_AVAILABLE, index=True,
    )
    # FK to the pending/confirmed booking currently holding this seat (nullable)
    current_booking_id = db.Column(
        db.Integer, db.ForeignKey("bookings.booking_id", ondelete="SET NULL"), nullable=True
    )

    schedule = db.relationship("FlightSchedule", back_populates="seats")

    @property
    def is_selectable(self) -> bool:
        return self.status == self.STATUS_AVAILABLE

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Seat {self.seat_number} {self.status}>"

"""Dated flight schedule (a flight operating on a specific date/time)."""
from datetime import datetime

from app.extensions import db


class FlightSchedule(db.Model):
    __tablename__ = "flight_schedules"
    __table_args__ = (
        db.Index("ix_schedule_route_time", "departure_time"),
    )

    STATUS_SCHEDULED = "SCHEDULED"
    STATUS_DEPARTED = "DEPARTED"
    STATUS_CANCELLED = "CANCELLED"
    STATUS_COMPLETED = "COMPLETED"

    schedule_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flight_id = db.Column(
        db.Integer, db.ForeignKey("flights.flight_id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    departure_time = db.Column(db.DateTime, nullable=False, index=True)
    arrival_time = db.Column(db.DateTime, nullable=False)
    base_fare = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(
        db.Enum("SCHEDULED", "DEPARTED", "CANCELLED", "COMPLETED", name="schedule_status"),
        nullable=False,
        default=STATUS_SCHEDULED,
        index=True,
    )
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    flight = db.relationship("Flight", back_populates="schedules")
    seats = db.relationship(
        "Seat", back_populates="schedule", cascade="all, delete-orphan", lazy="selectin"
    )

    # ---- derived helpers --------------------------------------------------
    @property
    def duration_minutes(self) -> int:
        if not self.arrival_time or not self.departure_time:
            return 0
        return int((self.arrival_time - self.departure_time).total_seconds() // 60)

    @property
    def duration_label(self) -> str:
        minutes = self.duration_minutes
        return f"{minutes // 60}h {minutes % 60:02d}m"

    @property
    def total_seats(self) -> int:
        return len(self.seats)

    @property
    def available_seats(self) -> int:
        return sum(1 for seat in self.seats if seat.status == "AVAILABLE")

    @property
    def economy_fare(self):
        return self.base_fare

    @property
    def business_fare(self):
        return round(float(self.base_fare) * 2.4, 2)

    def seat_price(self, seat_class: str):
        multiplier = {"ECONOMY": 1.0, "BUSINESS": 2.4, "FIRST": 3.6}.get(seat_class, 1.0)
        return round(float(self.base_fare) * multiplier, 2)

    def __repr__(self) -> str:  # pragma: no cover
        return f"<FlightSchedule {self.schedule_id} {self.departure_time:%Y-%m-%d %H:%M}>"

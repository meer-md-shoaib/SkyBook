"""Flight (route definition) model."""
from app.extensions import db


class Flight(db.Model):
    __tablename__ = "flights"
    __table_args__ = (
        db.CheckConstraint(
            "source_airport_id <> destination_airport_id",
            name="ck_flight_distinct_airports",
        ),
    )

    flight_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    flight_number = db.Column(db.String(10), nullable=False, unique=True, index=True)
    airline_name = db.Column(db.String(80), nullable=False)
    source_airport_id = db.Column(
        db.Integer, db.ForeignKey("airports.airport_id"), nullable=False, index=True
    )
    destination_airport_id = db.Column(
        db.Integer, db.ForeignKey("airports.airport_id"), nullable=False, index=True
    )
    aircraft_type = db.Column(db.String(40), nullable=False, default="Airbus A320")
    is_active = db.Column(db.Boolean, nullable=False, default=True)

    source_airport = db.relationship("Airport", foreign_keys=[source_airport_id])
    destination_airport = db.relationship("Airport", foreign_keys=[destination_airport_id])
    schedules = db.relationship(
        "FlightSchedule", back_populates="flight", cascade="all, delete-orphan", lazy="dynamic"
    )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Flight {self.flight_number}>"

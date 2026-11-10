"""Passenger details attached to a booking."""
from app.extensions import db


class Passenger(db.Model):
    __tablename__ = "passengers"

    ID_TYPES = ("AADHAAR", "PASSPORT", "DRIVING_LICENSE", "VOTER_ID")

    passenger_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    booking_id = db.Column(
        db.Integer, db.ForeignKey("bookings.booking_id", ondelete="CASCADE"),
        nullable=False, index=True,
    )
    full_name = db.Column(db.String(120), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(
        db.Enum("MALE", "FEMALE", "OTHER", name="passenger_gender"),
        nullable=False, default="OTHER",
    )
    identification_type = db.Column(db.String(30), nullable=False)
    identification_number = db.Column(db.String(40), nullable=False)
    seat_id = db.Column(
        db.Integer, db.ForeignKey("seats.seat_id", ondelete="SET NULL"), nullable=True
    )

    booking = db.relationship("Booking", back_populates="passengers")
    seat = db.relationship("Seat")

    @property
    def masked_id(self) -> str:
        """Never render raw identification numbers in listings."""
        if not self.identification_number:
            return "—"
        tail = self.identification_number[-4:]
        return f"••••{tail}"

    @property
    def age(self) -> int:
        from datetime import date

        if not self.date_of_birth:
            return 0
        today = date.today()
        return (
            today.year
            - self.date_of_birth.year
            - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
        )

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Passenger {self.full_name}>"

"""Airport lookup model."""
from app.extensions import db


class Airport(db.Model):
    __tablename__ = "airports"

    airport_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    airport_code = db.Column(db.String(3), nullable=False, unique=True, index=True)
    airport_name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(80), nullable=False, index=True)
    country = db.Column(db.String(80), nullable=False, default="India")

    def label(self) -> str:
        return f"{self.city} ({self.airport_code})"

    def __repr__(self) -> str:  # pragma: no cover
        return f"<Airport {self.airport_code}>"

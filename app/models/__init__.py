"""Model package — import every model so SQLAlchemy registers the metadata."""
from app.models.airport import Airport
from app.models.booking import Booking, BookingSeat
from app.models.cancellation import Cancellation
from app.models.flight import Flight
from app.models.passenger import Passenger
from app.models.payment import Payment
from app.models.schedule import FlightSchedule
from app.models.seat import Seat
from app.models.ticket import Ticket
from app.models.user import User

__all__ = [
    "Airport",
    "Booking",
    "BookingSeat",
    "Cancellation",
    "Flight",
    "FlightSchedule",
    "Passenger",
    "Payment",
    "Seat",
    "Ticket",
    "User",
]

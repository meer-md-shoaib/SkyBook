"""Seat inventory generation for a flight schedule."""
from app.extensions import db
from app.models import Seat


class SeatLayoutError(Exception):
    pass


class SeatService:
    BUSINESS_COLUMNS = ("A", "C", "D", "F")
    ECONOMY_COLUMNS = ("A", "B", "C", "D", "E", "F")

    @classmethod
    def generate(cls, schedule, business_rows: int = 3, economy_rows: int = 20,
                 replace: bool = False) -> int:
        """Create the seat inventory for ``schedule``. Returns seats created."""
        business_rows = max(0, min(int(business_rows), 8))
        economy_rows = max(1, min(int(economy_rows), 40))

        existing = Seat.query.filter_by(schedule_id=schedule.schedule_id).count()
        if existing:
            if not replace:
                return 0
            if Seat.query.filter(
                Seat.schedule_id == schedule.schedule_id, Seat.status != Seat.STATUS_AVAILABLE
            ).count():
                raise SeatLayoutError(
                    "Cannot regenerate seats: some seats are held or booked."
                )
            Seat.query.filter_by(schedule_id=schedule.schedule_id).delete()
            db.session.flush()

        seats = []
        for row in range(1, business_rows + 1):
            for column in cls.BUSINESS_COLUMNS:
                seats.append(
                    Seat(
                        schedule_id=schedule.schedule_id,
                        seat_number=f"{row}{column}",
                        seat_class="BUSINESS",
                        seat_row=row,
                        seat_column=column,
                        status=Seat.STATUS_AVAILABLE,
                    )
                )
        for row in range(business_rows + 1, business_rows + economy_rows + 1):
            for column in cls.ECONOMY_COLUMNS:
                seats.append(
                    Seat(
                        schedule_id=schedule.schedule_id,
                        seat_number=f"{row}{column}",
                        seat_class="ECONOMY",
                        seat_row=row,
                        seat_column=column,
                        status=Seat.STATUS_AVAILABLE,
                    )
                )
        db.session.add_all(seats)
        return len(seats)

    @staticmethod
    def counts(schedule_id: int) -> dict:
        seats = Seat.query.filter_by(schedule_id=schedule_id).all()
        return {
            "total": len(seats),
            "business": sum(1 for s in seats if s.seat_class == "BUSINESS"),
            "economy": sum(1 for s in seats if s.seat_class == "ECONOMY"),
            "available": sum(1 for s in seats if s.status == Seat.STATUS_AVAILABLE),
            "held": sum(1 for s in seats if s.status == Seat.STATUS_HELD),
            "booked": sum(1 for s in seats if s.status == Seat.STATUS_BOOKED),
        }

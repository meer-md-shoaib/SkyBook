"""Small formatting / presentation helpers used by templates and services."""
from datetime import datetime, timezone


def utcnow() -> datetime:
    """Return current naive UTC datetime (replaces deprecated datetime.utcnow())."""
    return datetime.now(timezone.utc).replace(tzinfo=None)



def format_currency(amount) -> str:
    """Format a number as Indian rupees, e.g. 4520.0 -> '₹4,520'."""
    try:
        value = float(amount)
    except (TypeError, ValueError):
        return "₹0"
    return "₹{:,.0f}".format(value)


def format_time(dt: datetime | None) -> str:
    return dt.strftime("%I:%M %p") if dt else "—"


def format_date(dt: datetime | None) -> str:
    return dt.strftime("%d %b %Y") if dt else "—"


def format_datetime(dt: datetime | None) -> str:
    return dt.strftime("%d %b %Y, %I:%M %p") if dt else "—"


def format_duration(minutes: int) -> str:
    if not minutes:
        return "—"
    return f"{minutes // 60}h {minutes % 60:02d}m"


def badge_class(status: str) -> str:
    """Map a booking/payment status to a CSS badge modifier."""
    mapping = {
        "PENDING": "warning",
        "CONFIRMED": "success",
        "CANCELLED": "danger",
        "EXPIRED": "muted",
        "SUCCESS": "success",
        "FAILED": "danger",
        "REFUNDED": "info",
        "PROCESSED": "success",
        "REJECTED": "danger",
        "AVAILABLE": "success",
        "HELD": "warning",
        "BOOKED": "muted",
        "SCHEDULED": "info",
        "DEPARTED": "muted",
        "COMPLETED": "success",
    }
    return mapping.get((status or "").upper(), "muted")


def initials(name: str) -> str:
    if not name:
        return "SB"
    parts = [p for p in name.split() if p]
    return "".join(p[0].upper() for p in parts[:2]) or "SB"


def build_seat_rows(seats) -> list[dict]:
    """Group seats into a row-based structure for the interactive seat map."""
    rows: dict[int, dict[str, object]] = {}
    for seat in seats:
        row = rows.setdefault(
            seat.seat_row, {"number": seat.seat_row, "seats": {}, "seat_class": seat.seat_class}
        )
        row["seats"][seat.seat_column] = seat
    ordered = []
    for number in sorted(rows):
        row = rows[number]
        ordered.append(
            {
                "number": row["number"],
                "seat_class": row["seat_class"],
                "columns": [row["seats"].get(col) for col in "ABCDEF"],
            }
        )
    return ordered


def parse_iso_date(value: str | None):
    """Parse 'YYYY-MM-DD' into a date, returning None on bad input."""
    if not value:
        return None
    try:
        return datetime.strptime(value.strip(), "%Y-%m-%d").date()
    except (ValueError, AttributeError):
        return None

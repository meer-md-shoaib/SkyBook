"""Server-side validation helpers for passenger and booking input."""
import re
from datetime import date

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[A-Za-z]{2,}$")
PHONE_RE = re.compile(r"^[+]?[0-9\s\-]{10,15}$")
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z .'\-]{1,79}$")
ID_NUMBER_RE = re.compile(r"^[A-Za-z0-9\-/]{5,30}$")

ID_TYPES = ("AADHAAR", "PASSPORT", "DRIVING_LICENSE", "VOTER_ID")
ID_TYPE_LABELS = {
    "AADHAAR": "Aadhaar",
    "PASSPORT": "Passport",
    "DRIVING_LICENSE": "Driving Licence",
    "VOTER_ID": "Voter ID",
}
GENDERS = ("MALE", "FEMALE", "OTHER")


def is_valid_email(value: str | None) -> bool:
    return bool(value and EMAIL_RE.match(value.strip()))


def is_valid_phone(value: str | None) -> bool:
    return bool(value and PHONE_RE.match(value.strip()))


def is_strong_password(value: str | None) -> bool:
    if not value or len(value) < 8:
        return False
    return (
        any(c.isdigit() for c in value)
        and any(c.isupper() for c in value)
        and any(c.islower() for c in value)
    )


def parse_date(value: str | None):
    if not value:
        return None
    try:
        return date.fromisoformat(value.strip())
    except (ValueError, AttributeError):
        return None


def validate_passenger(payload: dict) -> tuple[dict, list[str]]:
    """Normalise and validate one passenger payload.

    Returns ``(clean_data, errors)``. ``errors`` is empty when valid.
    """
    errors: list[str] = []
    full_name = (payload.get("full_name") or "").strip()
    if not NAME_RE.match(full_name):
        errors.append("Full name must be 2-80 letters (spaces and .'- allowed).")

    dob = parse_date(payload.get("date_of_birth"))
    if not dob:
        errors.append("A valid date of birth is required.")
    else:
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        if age < 1:
            errors.append("Passenger must be at least 1 year old.")
        elif age > 120:
            errors.append("Date of birth looks invalid.")

    gender = (payload.get("gender") or "").upper()
    if gender not in GENDERS:
        errors.append("Select a valid gender.")

    id_type = (payload.get("identification_type") or "").upper()
    if id_type not in ID_TYPES:
        errors.append("Select a valid identification type.")

    id_number = (payload.get("identification_number") or "").strip().upper()
    if not ID_NUMBER_RE.match(id_number):
        errors.append("Identification number must be 5-30 letters/digits.")

    clean = {
        "full_name": full_name,
        "date_of_birth": dob,
        "gender": gender,
        "identification_type": id_type,
        "identification_number": id_number,
    }
    return clean, errors


def validate_booking_contact(email: str | None, phone: str | None) -> list[str]:
    errors: list[str] = []
    if not is_valid_email(email):
        errors.append("Enter a valid contact email address.")
    if not is_valid_phone(phone):
        errors.append("Enter a valid contact phone number (10-15 digits).")
    return errors

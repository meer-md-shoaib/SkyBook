"""User account model (passengers and administrators)."""
from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import db, login_manager
from app.utils.helpers import utcnow


class User(UserMixin, db.Model):
    __tablename__ = "users"

    ROLE_PASSENGER = "PASSENGER"
    ROLE_ADMIN = "ADMIN"

    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    role = db.Column(
        db.Enum("PASSENGER", "ADMIN", name="user_role"),
        nullable=False,
        default=ROLE_PASSENGER,
        index=True,
    )
    is_active_flag = db.Column("is_active", db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utcnow)

    bookings = db.relationship(
        "Booking", back_populates="user", cascade="all, delete-orphan", lazy="dynamic"
    )

    # ---- password helpers -------------------------------------------------
    def set_password(self, raw_password: str) -> None:
        self.password_hash = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password_hash(self.password_hash, raw_password)

    # ---- flask-login ------------------------------------------------------
    def get_id(self):
        return str(self.user_id)

    @property
    def is_active(self):  # noqa: D401 - flask-login contract
        return bool(self.is_active_flag)

    @property
    def is_admin(self) -> bool:
        return self.role == self.ROLE_ADMIN

    def __repr__(self) -> str:  # pragma: no cover - debugging helper
        return f"<User {self.email} ({self.role})>"


@login_manager.user_loader
def load_user(user_id: str):
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None

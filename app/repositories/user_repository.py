"""User account data access."""
from app.extensions import db
from app.models import User


class UserRepository:
    @staticmethod
    def get_by_id(user_id: int) -> User | None:
        return db.session.get(User, int(user_id))

    @staticmethod
    def get_by_email(email: str) -> User | None:
        if not email:
            return None
        return User.query.filter(db.func.lower(User.email) == email.strip().lower()).first()

    @staticmethod
    def create(name: str, email: str, password: str, phone: str | None = None,
               role: str = User.ROLE_PASSENGER) -> User:
        user = User(name=name.strip(), email=email.strip().lower(), phone=phone, role=role)
        user.set_password(password)
        db.session.add(user)
        db.session.flush()
        return user

    @staticmethod
    def count_passengers() -> int:
        return User.query.filter_by(role=User.ROLE_PASSENGER).count()

    @staticmethod
    def list_passengers(limit: int = 100):
        return (
            User.query.filter_by(role=User.ROLE_PASSENGER)
            .order_by(User.created_at.desc())
            .limit(limit)
            .all()
        )

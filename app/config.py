"""Application configuration loaded from environment variables."""
import os
from datetime import timedelta


def _db_uri(name: str) -> str:
    """Build a PyMySQL SQLAlchemy URI from individual env vars."""
    user = os.getenv("DB_USER", "root")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    auth = f"{user}:{password}" if password else user
    return f"mysql+pymysql://{auth}@{host}:{port}/{name}?charset=utf8mb4"


class BaseConfig:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")

    # --- database -------------------------------------------------
    SQLALCHEMY_DATABASE_URI = _db_uri(os.getenv("DB_NAME", "skybook_db"))
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 3600,
        "isolation_level": "READ COMMITTED",
    }

    # --- auth / forms ---------------------------------------------
    WTF_CSRF_TIME_LIMIT = None
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    REMEMBER_COOKIE_DURATION = timedelta(days=7)

    # --- business rules -------------------------------------------
    SEAT_HOLD_MINUTES = int(os.getenv("SEAT_HOLD_MINUTES", "10"))
    CANCELLATION_FEE_PERCENT = float(os.getenv("CANCELLATION_FEE_PERCENT", "10"))
    TICKET_OUTPUT_DIR = os.getenv("TICKET_OUTPUT_DIR", "generated_tickets")

    # --- UI -------------------------------------------------------
    APP_NAME = "SkyBook"
    APP_TAGLINE = "Book Flights Seamlessly Across the Globe"


class DevelopmentConfig(BaseConfig):
    DEBUG = True
    ENV = "development"


class TestingConfig(BaseConfig):
    TESTING = True
    DEBUG = False
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = _db_uri(os.getenv("TEST_DB_NAME", "skybook_test_db"))
    SEAT_HOLD_MINUTES = 10


class ProductionConfig(BaseConfig):
    DEBUG = False
    ENV = "production"
    SESSION_COOKIE_SECURE = True


CONFIG_MAP = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
    "production": ProductionConfig,
}

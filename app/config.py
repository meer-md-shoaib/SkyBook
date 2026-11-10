"""Application configuration loaded from environment variables."""
import os
import urllib.parse
from datetime import timedelta


def _db_uri(name: str) -> str:
    """Build a PyMySQL SQLAlchemy URI from individual env vars or full URL."""
    uri = os.getenv("DATABASE_URL") or os.getenv("MYSQL_URL")
    if uri:
        if uri.startswith("mysql://"):
            uri = uri.replace("mysql://", "mysql+pymysql://", 1)
        if "tidbcloud.com" in uri and "ssl" not in uri:
            sep = "&" if "?" in uri else "?"
            uri = f"{uri}{sep}ssl_verify_cert=true"
        return uri
    raw_user = os.getenv("DB_USER", "root")
    raw_pass = os.getenv("DB_PASSWORD", "")
    user = urllib.parse.quote_plus(raw_user)
    password = urllib.parse.quote_plus(raw_pass)
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "3306")
    auth = f"{user}:{password}" if raw_pass else user
    ssl_extra = "&ssl_verify_cert=true" if "tidbcloud.com" in host else ""
    return f"mysql+pymysql://{auth}@{host}:{port}/{name}?charset=utf8mb4{ssl_extra}"


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
    SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "shoaibmeermd@gmail.com")


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

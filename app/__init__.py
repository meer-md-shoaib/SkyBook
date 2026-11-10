"""SkyBook application factory."""
import os
from datetime import datetime

import click
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user

from app.config import CONFIG_MAP
from app.extensions import csrf, db, login_manager


def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__, instance_relative_config=False)

    config_name = config_name or os.getenv("FLASK_ENV", "development")
    app.config.from_object(CONFIG_MAP.get(config_name, CONFIG_MAP["development"]))

    # Make sure ticket output folder exists.
    folder = app.config["TICKET_OUTPUT_DIR"]
    if not os.path.isabs(folder):
        folder = os.path.join(app.root_path, "..", folder)
    os.makedirs(os.path.abspath(folder), exist_ok=True)

    _init_extensions(app)
    _register_blueprints(app)
    _register_template_helpers(app)
    _register_error_handlers(app)
    _register_cli(app)

    @app.context_processor
    def inject_globals():
        from app.utils.helpers import (
            badge_class, format_currency, format_date, format_datetime,
            format_duration, format_time, initials, utcnow,
        )

        return {
            "APP_NAME": app.config["APP_NAME"],
            "APP_TAGLINE": app.config["APP_TAGLINE"],
            "current_year": utcnow().year,
            "now": utcnow(),
            "format_currency": format_currency,
            "format_time": format_time,
            "format_date": format_date,
            "format_datetime": format_datetime,
            "format_duration": format_duration,
            "badge_class": badge_class,
            "initials": initials,
        }

    return app


def _init_extensions(app: Flask) -> None:
    from app import models  # noqa: F401  (register models on the metadata)

    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)


def _register_blueprints(app: Flask) -> None:
    from app.routes.admin import admin_bp
    from app.routes.auth import auth_bp
    from app.routes.bookings import bookings_bp
    from app.routes.flights import flights_bp
    from app.routes.main import main_bp
    from app.routes.payments import payments_bp
    from app.routes.tickets import tickets_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(flights_bp, url_prefix="/flights")
    app.register_blueprint(bookings_bp, url_prefix="/bookings")
    app.register_blueprint(payments_bp, url_prefix="/payments")
    app.register_blueprint(tickets_bp, url_prefix="/tickets")
    app.register_blueprint(admin_bp, url_prefix="/admin")


def _register_template_helpers(app: Flask) -> None:
    @app.template_filter("inr")
    def inr_filter(value):
        from app.utils.helpers import format_currency

        return format_currency(value)

    @app.template_filter("time12")
    def time_filter(value):
        from app.utils.helpers import format_time

        return format_time(value)

    @app.template_filter("datefmt")
    def date_filter(value):
        from app.utils.helpers import format_date

        return format_date(value)

    @app.template_filter("datetimefmt")
    def datetime_filter(value):
        from app.utils.helpers import format_datetime

        return format_datetime(value)

    @app.template_filter("duration")
    def duration_filter(value):
        from app.utils.helpers import format_duration

        return format_duration(value)


def _register_error_handlers(app: Flask) -> None:
    @app.errorhandler(403)
    def forbidden(error):
        if request.path.startswith("/admin"):
            flash("Administrator privileges are required for that page.", "danger")
            return redirect(url_for("main.index"))
        return render_template("errors/403.html"), 403

    @app.errorhandler(404)
    def not_found(error):
        return render_template("errors/404.html"), 404

    @app.errorhandler(500)
    def server_error(error):  # pragma: no cover - defensive
        db.session.rollback()
        app.logger.exception("Unhandled error: %s", error)
        return render_template("errors/500.html"), 500

    @app.errorhandler(400)
    def bad_request(error):
        return render_template("errors/400.html"), 400


def _register_cli(app: Flask) -> None:
    @app.cli.command("init-db")
    def init_db():
        """Create all tables from the SQLAlchemy metadata."""
        db.create_all()
        click.echo("Database tables created.")

    @app.cli.command("seed-db")
    def seed_db():
        """Load demo airports, flights, schedules, seats and accounts."""
        from app.seed import seed_database

        result = seed_database()
        click.echo(result)

    @app.cli.command("reset-db")
    def reset_db():
        """Drop and recreate every table, then seed demo data."""
        from app.seed import seed_database

        db.drop_all()
        db.create_all()
        click.echo(seed_database())

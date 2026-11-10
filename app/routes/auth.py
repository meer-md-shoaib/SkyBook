"""Registration, login and logout."""
from urllib.parse import urlparse

from flask import Blueprint, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_user, logout_user
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.forms import LoginForm, RegisterForm
from app.repositories.user_repository import UserRepository
from app.utils.validators import is_strong_password

auth_bp = Blueprint("auth", __name__)


def _safe_next(target: str | None) -> str | None:
    if not target:
        return None
    parsed = urlparse(target)
    if parsed.netloc or parsed.scheme:
        return None
    return target


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = RegisterForm()
    if form.validate_on_submit():
        if UserRepository.get_by_email(form.email.data):
            flash("An account with that email already exists. Try signing in.", "danger")
            return render_template("register.html", form=form)

        if not is_strong_password(form.password.data):
            flash("Password must be at least 8 characters and include uppercase, lowercase, and a number.", "danger")
            return render_template("register.html", form=form)

        user = UserRepository.create(
            name=form.name.data,
            email=form.email.data,
            password=form.password.data,
            phone=form.phone.data,
        )
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            flash("We could not create your account. Please try again.", "danger")
            return render_template("register.html", form=form)

        login_user(user)
        flash(f"Welcome aboard, {user.name.split()[0]}! Your SkyBook account is ready.", "success")
        return redirect(url_for("main.index"))

    for field, messages in form.errors.items():
        label = getattr(form, field).label.text
        for message in messages:
            flash(f"{label}: {message}", "danger")
    return render_template("register.html", form=form)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("main.index"))

    form = LoginForm()
    if form.validate_on_submit():
        user = UserRepository.get_by_email(form.email.data)
        if user is None or not user.check_password(form.password.data):
            flash("Incorrect email or password. Please try again.", "danger")
            return render_template("login.html", form=form)
        if not user.is_active:
            flash("This account has been disabled. Contact support.", "danger")
            return render_template("login.html", form=form)

        login_user(user, remember=form.remember.data)
        flash(f"Signed in as {user.name}.", "success")

        if user.is_admin:
            return redirect(url_for("admin.dashboard"))
        target = _safe_next(request.args.get("next")) or url_for("main.index")
        return redirect(target)

    for field, messages in form.errors.items():
        for message in messages:
            flash(message, "danger")
    return render_template("login.html", form=form)


@auth_bp.route("/logout", methods=["POST"])
def logout():
    if current_user.is_authenticated:
        logout_user()
        flash("You have been signed out.", "info")
    return redirect(url_for("main.index"))

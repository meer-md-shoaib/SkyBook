"""Route decorators for role based access control."""
from functools import wraps

from flask import abort, flash, redirect, url_for
from flask_login import current_user


def admin_required(view):
    """Allow only authenticated administrators; reject everyone else."""

    @wraps(view)
    def wrapper(*args, **kwargs):
        if not current_user.is_authenticated:
            flash("Please sign in with an administrator account.", "warning")
            return redirect(url_for("auth.login", next="admin"))
        if not getattr(current_user, "is_admin", False):
            abort(403)
        return view(*args, **kwargs)

    return wrapper

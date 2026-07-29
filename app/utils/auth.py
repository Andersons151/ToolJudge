from functools import wraps
from flask import session, redirect, url_for, flash


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please log in to access the admin area.", "warning")
            return redirect(url_for("admin.login"))
        return view_func(*args, **kwargs)
    return wrapper

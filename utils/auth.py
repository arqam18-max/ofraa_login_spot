from functools import wraps
from flask import redirect, session, url_for


def login_required(view):
    """ログインしていなければログイン画面へ移動する"""
    @wraps(view)
    def wrapped(*args, **kwargs):
        if "admin_id" not in session:
            return redirect(url_for("login.login"))
        return view(*args, **kwargs)
    return wrapped

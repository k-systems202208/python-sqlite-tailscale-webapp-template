import hmac
import secrets

from flask import abort, request, session

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}


def csrf_token() -> str:
    token = session.get("_csrf_token")
    if not token:
        token = secrets.token_urlsafe(32)
        session["_csrf_token"] = token
    return token


def install_csrf(app) -> None:
    app.jinja_env.globals["csrf_token"] = csrf_token

    @app.before_request
    def validate_csrf():
        if request.method in SAFE_METHODS:
            return None

        expected = session.get("_csrf_token")
        supplied = request.headers.get("X-CSRF-Token") or request.form.get("csrf_token")
        if not expected or not supplied or not hmac.compare_digest(expected, supplied):
            abort(400, description="Invalid or missing CSRF token")

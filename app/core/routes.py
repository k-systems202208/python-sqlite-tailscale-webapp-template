import sqlite3

from flask import Blueprint, current_app, g, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

from app.db import get_db

from .access import require_user

bp = Blueprint("core", __name__, template_folder="templates")


@bp.get("/")
@require_user
def index():
    return render_template(
        "core/index.html",
        items_sample_enabled="items.index" in current_app.view_functions,
    )


@bp.get("/healthz")
def healthz():
    return jsonify({"status": "ok", "app": current_app.config["APP_NAME"]})


@bp.get("/readyz")
def readyz():
    try:
        get_db().execute("SELECT 1").fetchone()
    except sqlite3.Error:
        current_app.logger.exception("SQLite readiness check failed")
        return jsonify({"status": "not_ready", "database": "error"}), 503
    return jsonify({"status": "ready", "database": "ok"})


@bp.get("/api/me")
@require_user
def api_me():
    return jsonify(
        {
            "login": g.current_user["login"],
            "display_name": g.current_user["display_name"],
            "source": g.current_user["identity_source"],
        }
    )


@bp.app_errorhandler(HTTPException)
def http_error(error: HTTPException):
    if request.path.startswith("/api/"):
        return jsonify({"error": error.description, "status": error.code}), error.code
    if error.code == 401:
        return render_template("unauthorized.html"), 401
    return error

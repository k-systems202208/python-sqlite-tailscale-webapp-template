from functools import wraps

from flask import Blueprint, abort, current_app, g, jsonify, redirect, render_template, request, url_for

from .services.items import create_item, delete_item, list_items, toggle_item

bp = Blueprint("main", __name__)


def require_user(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if g.current_user is None:
            abort(401)
        return view(*args, **kwargs)
    return wrapped


def _item_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "body": row["body"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@bp.get("/healthz")
def healthz():
    return jsonify({"status": "ok", "app": current_app.config["APP_NAME"]})


@bp.get("/")
@require_user
def index():
    rows = list_items(g.current_user["id"])
    return render_template("index.html", items=rows)


@bp.post("/items")
@require_user
def add_item():
    try:
        create_item(g.current_user["id"], request.form.get("title", ""), request.form.get("body", ""))
    except ValueError as exc:
        abort(400, description=str(exc))
    return redirect(url_for("main.index"))


@bp.post("/items/<int:item_id>/toggle")
@require_user
def toggle(item_id: int):
    if not toggle_item(g.current_user["id"], item_id):
        abort(404)
    return redirect(url_for("main.index"))


@bp.post("/items/<int:item_id>/delete")
@require_user
def delete(item_id: int):
    if not delete_item(g.current_user["id"], item_id):
        abort(404)
    return redirect(url_for("main.index"))


@bp.get("/api/me")
@require_user
def api_me():
    return jsonify({
        "login": g.current_user["login"],
        "display_name": g.current_user["display_name"],
        "source": g.current_user["identity_source"],
    })


@bp.get("/api/items")
@require_user
def api_items():
    return jsonify([_item_to_dict(row) for row in list_items(g.current_user["id"])])


@bp.post("/api/items")
@require_user
def api_create_item():
    payload = request.get_json(silent=True) or {}
    try:
        row = create_item(g.current_user["id"], payload.get("title", ""), payload.get("body", ""))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    return jsonify(_item_to_dict(row)), 201


@bp.app_errorhandler(401)
def unauthorized(_error):
    if request.path.startswith("/api/"):
        return jsonify({"error": "authentication required"}), 401
    return render_template("unauthorized.html"), 401

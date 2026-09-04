from flask import (
    Blueprint,
    abort,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    url_for,
)

from app.core.access import require_user

from .service import create_item, delete_item, list_items, toggle_item

bp = Blueprint("items", __name__, template_folder="templates")


def _item_to_dict(row):
    return {
        "id": row["id"],
        "title": row["title"],
        "body": row["body"],
        "status": row["status"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


@bp.get("/items")
@require_user
def index():
    rows = list_items(g.current_user["id"])
    return render_template("items/index.html", items=rows)


@bp.post("/items")
@require_user
def add_item():
    try:
        create_item(
            g.current_user["id"],
            request.form.get("title", ""),
            request.form.get("body", ""),
        )
    except ValueError as exc:
        abort(400, description=str(exc))
    return redirect(url_for("items.index"))


@bp.post("/items/<int:item_id>/toggle")
@require_user
def toggle(item_id: int):
    if not toggle_item(g.current_user["id"], item_id):
        abort(404)
    return redirect(url_for("items.index"))


@bp.post("/items/<int:item_id>/delete")
@require_user
def delete(item_id: int):
    if not delete_item(g.current_user["id"], item_id):
        abort(404)
    return redirect(url_for("items.index"))


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
        abort(400, description=str(exc))
    return jsonify(_item_to_dict(row)), 201

from flask import Blueprint, request, jsonify
from core.db import db

bp = Blueprint("groups", __name__, url_prefix="/api/groups")

@bp.get("/")
def all_groups():
    with db() as conn:
        rows = conn.execute("SELECT * FROM groups").fetchall()
    return jsonify([dict(x) for x in rows])

@bp.post("/")
def create_group():
    data = request.json
    name = data.get("name", "New Group")

    with db() as conn:
        cur = conn.execute(
            "INSERT INTO groups(name) VALUES(?)",
            (name,)
        )
        gid = cur.lastrowid

    return jsonify({"id": gid, "name": name})
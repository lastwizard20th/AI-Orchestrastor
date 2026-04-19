from flask import Blueprint, request, jsonify, Response
from services.team_engine import run_group, stream_events

bp = Blueprint("team", __name__, url_prefix="/api/team")

@bp.post("/run")
def run_team():
    data = request.json or {}
    group_id = int(data.get("group_id", 1))
    message = data.get("message", "")

    result = run_group(group_id, message)
    return jsonify(result)

@bp.get("/stream/<run_id>")
def stream(run_id):
    return Response(
        stream_events(run_id),
        mimetype="text/event-stream"
    )
from flask import Blueprint, request, jsonify
from services.avatar_service import get_avatar
from services.speech_bus import get_events, is_busy

realtime_bp = Blueprint("realtime", __name__)

@realtime_bp.route("/avatar/state")
def avatar_state():
    return jsonify(get_avatar())

@realtime_bp.route("/speech/events")
def speech_events():
    after = float(request.args.get("after", 0))
    return jsonify({
        "busy": is_busy(),
        "events": get_events(after)
    })
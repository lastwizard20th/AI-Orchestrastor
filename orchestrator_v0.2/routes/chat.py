from flask import Blueprint, request, jsonify, render_template
from services.orchestrator import handle_chat
from services.history_service import list_history

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/')
def home():
    return render_template('index.html')

@chat_bp.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(force=True)

    result = handle_chat(
        message=data.get("message", ""),
        session_id=data.get("session_id", "default"),
        mode=data.get("mode", "auto"),
        profile=data.get("profile", "default"),
        room_type=data.get("room_type", "private"),
    )

    return jsonify(result)

@chat_bp.route('/history/<session_id>')
def history(session_id):
    return jsonify(list_history(session_id))
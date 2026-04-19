from flask import Blueprint, request, jsonify
from services.model_service import *

model_bp = Blueprint("models2", __name__)


@model_bp.route("/models")
def models():
    return jsonify(list_models())


@model_bp.route("/model/add", methods=["POST"])
def model_add():
    d = request.get_json(force=True)
    add_model(
        int(d["provider_id"]),
        d["alias"],
        d["model_name"],
        d.get("role", "core")
    )
    return jsonify({"ok": True})
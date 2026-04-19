from flask import Blueprint, request, jsonify

from services.provider_manager import (
    load_all,
    get_provider,
    save_provider,
    delete_provider,
    test_provider
)

provider_bp = Blueprint("providers", __name__)


@provider_bp.route("/providers")
def providers():
    return jsonify(load_all())


@provider_bp.route("/provider/<name>")
def provider(name):
    return jsonify(get_provider(name) or {})


@provider_bp.route("/provider/save", methods=["POST"])
def provider_save():
    data = request.get_json(force=True)
    save_provider(data)
    return jsonify({"ok": True})


@provider_bp.route("/provider/delete", methods=["POST"])
def provider_delete_route():
    data = request.get_json(force=True)
    delete_provider(data.get("name", ""))
    return jsonify({"ok": True})


@provider_bp.route("/provider/test", methods=["POST"])
def provider_test_route():
    data = request.get_json(force=True)
    return jsonify(test_provider(data.get("name", "")))
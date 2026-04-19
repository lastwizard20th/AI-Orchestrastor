from flask import Blueprint, request, jsonify
from services.settings import load_all, get_profile, save_profile, delete_profile

settings_bp = Blueprint('settings', __name__)

@settings_bp.route('/profiles')
def profiles():
    return jsonify(load_all())

@settings_bp.route('/profile/<name>')
def profile(name):
    return jsonify(get_profile(name))

@settings_bp.route('/profile/save', methods=['POST'])
def profile_save():
    data = request.get_json(force=True)
    save_profile(
        data.get('name', 'default'),
        data.get('config', {})
    )
    return jsonify({'ok': True})

@settings_bp.route('/profile/delete', methods=['POST'])
def profile_delete_route():
    data = request.get_json(force=True)
    delete_profile(data.get('name', ''))
    return jsonify({'ok': True})
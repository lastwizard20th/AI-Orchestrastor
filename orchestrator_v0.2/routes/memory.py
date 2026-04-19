from flask import Blueprint, request, jsonify
from services.memory_service import (
    get_all_memories,
    delete_memory,
    search_memory,
    save_memory_async,
)

memory_bp = Blueprint('memory', __name__)

@memory_bp.route('/memories')
def memories():
    return jsonify(get_all_memories())

@memory_bp.route('/memory/search', methods=['POST'])
def memory_search():
    d = request.get_json(force=True)
    q = d.get('query','')
    return jsonify({'result': search_memory(q)})

@memory_bp.route('/memory/add', methods=['POST'])
def memory_add():
    d = request.get_json(force=True)
    save_memory_async(d.get('text',''))
    return jsonify({'ok': True})

@memory_bp.route('/memory/delete', methods=['POST'])
def memory_delete_route():
    d = request.get_json(force=True)
    delete_memory(int(d.get('id')))
    return jsonify({'ok': True})
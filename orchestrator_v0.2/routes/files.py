from flask import Blueprint, request, jsonify
from tools.file_tool import (
    list_files,
    read_file,
    write_file,
    delete_file,
    make_folder,
    file_info,
)

file_bp = Blueprint('files', __name__)

@file_bp.route('/files')
def files():
    path = request.args.get('path', '')
    return jsonify(list_files(path))

@file_bp.route('/file/read')
def file_read():
    path = request.args.get('path', '')
    return jsonify({'content': read_file(path)})

@file_bp.route('/file/write', methods=['POST'])
def file_write():
    data = request.get_json(force=True)
    result = write_file(data.get('path', ''), data.get('content', ''))
    return jsonify({'result': result})

@file_bp.route('/file/delete', methods=['POST'])
def file_delete_route():
    data = request.get_json(force=True)
    result = delete_file(data.get('path', ''))
    return jsonify({'result': result})

@file_bp.route('/folder/create', methods=['POST'])
def folder_create():
    data = request.get_json(force=True)
    result = make_folder(data.get('path', ''))
    return jsonify({'result': result})

@file_bp.route('/file/info')
def file_info_route():
    path = request.args.get('path', '')
    return jsonify(file_info(path))
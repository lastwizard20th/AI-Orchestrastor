from flask import Blueprint, request, jsonify
from services.tasks import add_task, list_tasks, delete_task
from services.executor import run_pending, run_task
from services.tasks import move_task, update_task, resize_task
task_bp = Blueprint('tasks', __name__)

def _find(task_id):
    for t in list_tasks():
        if t['id'] == task_id:
            return t
    return None

@task_bp.route('/tasks')
def tasks():
    return jsonify(list_tasks())

@task_bp.route('/task/add', methods=['POST'])
def task_add():
    d = request.get_json(force=True)
    add_task(
        title=d.get('title','Untitled'),
        priority=d.get('priority','medium'),
        notes=d.get('notes',''),
        agent=d.get('agent','auto'),
        day_index=d.get('day_index',0),
        start_slot=d.get('start_slot',18),
        duration_slots=d.get('duration_slots',2)
    )
    return jsonify({'ok': True})

@task_bp.route('/task/delete', methods=['POST'])
def task_delete():
    d = request.get_json(force=True)
    delete_task(int(d.get('id')))
    return jsonify({'ok': True})

@task_bp.route('/task/run', methods=['POST'])
def task_run():
    d = request.get_json(force=True)
    task = _find(int(d.get('id')))
    if not task:
        return jsonify({'ok': False, 'error': 'Task not found'}), 404
    return jsonify(run_task(task))

@task_bp.route('/tasks/run_pending', methods=['POST'])
def tasks_run_pending():
    return jsonify(run_pending())

@task_bp.route('/planner')
def planner_page():
    from flask import render_template
    return render_template('planner.html')

@task_bp.route('/task/update', methods=['POST'])
def task_update():
    d=request.get_json(force=True)
    update_task(int(d['id']), d.get('title'), d.get('status'))
    return jsonify({'ok':True})

@task_bp.route('/task/move', methods=['POST'])
def task_move():
    d=request.get_json(force=True)
    move_task(int(d['id']), int(d['day_index']), int(d['start_slot']))
    return jsonify({'ok':True})

@task_bp.route('/task/resize', methods=['POST'])
def task_resize():
    d=request.get_json(force=True)
    resize_task(int(d['id']), int(d['duration_slots']))
    return jsonify({'ok':True})
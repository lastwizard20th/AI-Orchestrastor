import time
from core.db import get_conn

def add_task(title, priority='medium', notes='', agent='auto', due_at='', day_index=0, start_slot=18, duration_slots=2):
    now=time.time()
    c=get_conn()
    c.execute('''INSERT INTO tasks(title,status,priority,notes,result,agent,due_at,created_at,updated_at)
                 VALUES(?,?,?,?,?,?,?,?,?)''',
                 (title,'todo',priority,notes,'',agent,due_at,now,now))
    c.commit(); c.close()

def list_tasks():
    c=get_conn(); rows=c.execute('SELECT * FROM tasks ORDER BY id DESC').fetchall(); c.close()
    return [dict(r) for r in rows]

def save_result(task_id, result, status='done'):
    c=get_conn()
    c.execute('UPDATE tasks SET result=?, status=?, updated_at=? WHERE id=?', (result,status,time.time(),task_id))
    c.commit(); c.close()

def delete_task(task_id):
    c=get_conn(); c.execute('DELETE FROM tasks WHERE id=?',(task_id,)); c.commit(); c.close()

def update_task(task_id, title=None, status=None):
    fields=[]; vals=[]
    if title is not None: fields.append('title=?'); vals.append(title)
    if status is not None: fields.append('status=?'); vals.append(status)
    fields.append('updated_at=?'); vals.append(time.time())
    vals.append(task_id)
    c=get_conn(); c.execute(f"UPDATE tasks SET {','.join(fields)} WHERE id=?", vals); c.commit(); c.close()

def move_task(task_id, day_index, start_slot):
    c=get_conn()
    c.execute('UPDATE tasks SET day_index=?, start_slot=?, updated_at=? WHERE id=?',(day_index,start_slot,time.time(),task_id))
    c.commit(); c.close()

def resize_task(task_id, duration_slots):
    c=get_conn()
    c.execute('UPDATE tasks SET duration_slots=?, updated_at=? WHERE id=?', (duration_slots, time.time(), task_id))
    c.commit(); c.close()
import time
from core.db import db

def add_history(session_id, role, text):
    with db() as conn:
        conn.execute(
            'INSERT INTO history(session_id,role,text,ts) VALUES(?,?,?,?)',
            (session_id, role, text, time.time())
        )

def list_history(session_id, limit=100):
    with db() as conn:
        rows = conn.execute(
            'SELECT role,text,ts FROM history WHERE session_id=? ORDER BY id ASC LIMIT ?',
            (session_id, limit)
        ).fetchall()
    return [dict(r) for r in rows]

def get_recent(session_id, limit=8):
    with db() as conn:
        rows = conn.execute(
            'SELECT role,text FROM history WHERE session_id=? ORDER BY id DESC LIMIT ?',
            (session_id, limit)
        ).fetchall()
    rows = rows[::-1]
    return ''.join(f"{r['role']}: {r['text']}" for r in rows)
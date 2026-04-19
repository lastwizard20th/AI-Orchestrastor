import time
from core.db import db


def list_providers():
    with db() as c:
        rows = c.execute("SELECT * FROM providers ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]


def add_provider(name, ptype, endpoint="", api_key=""):
    with db() as c:
        c.execute("""
            INSERT INTO providers(name,type,endpoint,api_key,created_at)
            VALUES(?,?,?,?,?)
        """, (name, ptype, endpoint, api_key, time.time()))


def delete_provider(pid):
    with db() as c:
        c.execute("DELETE FROM providers WHERE id=?", (pid,))


def get_provider(pid):
    with db() as c:
        row = c.execute("SELECT * FROM providers WHERE id=?", (pid,)).fetchone()
    return dict(row) if row else None
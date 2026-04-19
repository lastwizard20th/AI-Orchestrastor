from core.db import db


def list_models():
    with db() as c:
        rows = c.execute("""
            SELECT m.*, p.name provider_name
            FROM models m
            JOIN providers p ON p.id=m.provider_id
            ORDER BY m.id DESC
        """).fetchall()
    return [dict(r) for r in rows]


def add_model(provider_id, alias, model_name, role="core"):
    with db() as c:
        c.execute("""
            INSERT INTO models(provider_id,alias,model_name,role)
            VALUES(?,?,?,?)
        """, (provider_id, alias, model_name, role))


def update_model(mid, system_prompt="", personality="", temperature=0.4, max_tokens=2048):
    with db() as c:
        c.execute("""
            UPDATE models
            SET system_prompt=?, personality=?, temperature=?, max_tokens=?
            WHERE id=?
        """, (system_prompt, personality, temperature, max_tokens, mid))


def get_model(mid):
    with db() as c:
        row = c.execute("SELECT * FROM models WHERE id=?", (mid,)).fetchone()
    return dict(row) if row else None
from core.db import db

with db() as conn:
    conn.execute("""
    CREATE TABLE IF NOT EXISTS groups(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS nodes(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        label TEXT,
        node_role TEXT,
        model_id INTEGER,
        system_prompt TEXT
    )
    """)

    conn.execute("""
    CREATE TABLE IF NOT EXISTS edges(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER,
        source_id INTEGER,
        target_id INTEGER,
        edge_type TEXT
    )
    """)
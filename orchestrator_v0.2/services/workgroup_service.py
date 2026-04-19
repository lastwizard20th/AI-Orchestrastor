import time
from core.db import db


# ==================================================
# WORKGROUP
# ==================================================

def create_workgroup(name):
    with db() as conn:
        cur = conn.execute(
            """
            INSERT INTO workgroups(name, created_at)
            VALUES(?, ?)
            """,
            (name, time.time())
        )
        return cur.lastrowid


def list_workgroups():
    with db() as conn:
        rows = conn.execute(
            """
            SELECT *
            FROM workgroups
            ORDER BY id DESC
            """
        ).fetchall()

    return [dict(r) for r in rows]


def delete_workgroup(wid):
    with db() as conn:
        conn.execute("DELETE FROM edges WHERE group_id=?", (wid,))
        conn.execute("DELETE FROM nodes WHERE group_id=?", (wid,))
        conn.execute("DELETE FROM workgroups WHERE id=?", (wid,))


# ==================================================
# NODES
# ==================================================

def add_node(
    group_id,
    model_id,
    label,
    node_role,
    x=100,
    y=100,
    system_prompt=""
):
    with db() as conn:
        cur = conn.execute(
            """
            INSERT INTO nodes(
                group_id,
                model_id,
                label,
                node_role,
                x,
                y,
                system_prompt
            )
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                group_id,
                model_id,
                label,
                node_role,
                x,
                y,
                system_prompt
            )
        )
        return cur.lastrowid


def update_node(node_id, x, y):
    with db() as conn:
        conn.execute(
            """
            UPDATE nodes
            SET x=?, y=?
            WHERE id=?
            """,
            (x, y, node_id)
        )


def update_node_meta(node_id, label, node_role, system_prompt=""):
    with db() as conn:
        conn.execute(
            """
            UPDATE nodes
            SET label=?,
                node_role=?,
                system_prompt=?
            WHERE id=?
            """,
            (label, node_role, system_prompt, node_id)
        )


def delete_node(node_id):
    with db() as conn:
        conn.execute(
            "DELETE FROM edges WHERE source_id=? OR target_id=?",
            (node_id, node_id)
        )
        conn.execute(
            "DELETE FROM nodes WHERE id=?",
            (node_id,)
        )


# ==================================================
# EDGES
# ==================================================

def add_edge(group_id, source_id, target_id, edge_type="support"):
    with db() as conn:
        cur = conn.execute(
            """
            INSERT INTO edges(
                group_id,
                source_id,
                target_id,
                edge_type
            )
            VALUES(?,?,?,?)
            """,
            (
                group_id,
                source_id,
                target_id,
                edge_type
            )
        )
        return cur.lastrowid


def delete_edge(edge_id):
    with db() as conn:
        conn.execute(
            "DELETE FROM edges WHERE id=?",
            (edge_id,)
        )


# ==================================================
# GRAPH
# ==================================================

def get_graph(group_id):
    with db() as conn:
        nodes = conn.execute(
            """
            SELECT
                n.*,
                p.name AS provider_name
            FROM nodes n
            LEFT JOIN providers p
                ON p.id = n.model_id
            WHERE n.group_id=?
            ORDER BY n.id
            """,
            (group_id,)
        ).fetchall()

        edges = conn.execute(
            """
            SELECT *
            FROM edges
            WHERE group_id=?
            ORDER BY id
            """,
            (group_id,)
        ).fetchall()

    return {
        "nodes": [dict(x) for x in nodes],
        "edges": [dict(x) for x in edges]
    }
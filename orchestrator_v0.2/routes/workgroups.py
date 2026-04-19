# routes/workgroups.py

from flask import Blueprint, request, jsonify, render_template

from services.workgroup_service import (
    list_workgroups,
    create_workgroup,
    get_graph,
    add_node,
    update_node,
    add_edge,
)

from services.team_engine import run_group

workgroup_bp = Blueprint("workgroup", __name__)


# ==================================================
# UI PAGE
# ==================================================
@workgroup_bp.route("/builder")
def builder():
    return render_template("workgroup.html")


# ==================================================
# LIST GROUPS
# ==================================================
@workgroup_bp.route("/workgroups")
def groups():
    return jsonify(list_workgroups())


# ==================================================
# CREATE GROUP
# ==================================================
@workgroup_bp.route("/workgroup/create", methods=["POST"])
def create_group():
    d = request.get_json(force=True)

    name = d.get("name", "New Group")
    gid = create_workgroup(name)

    return jsonify({
        "ok": True,
        "id": gid
    })


# ==================================================
# LOAD GRAPH
# ==================================================
@workgroup_bp.route("/workgroup/<int:wid>")
def get_group_graph(wid):
    return jsonify(get_graph(wid))


# ==================================================
# ADD NODE
# ==================================================
@workgroup_bp.route("/node/add", methods=["POST"])
def node_add():
    d = request.get_json(force=True)

    nid = add_node(
        d["workgroup_id"],
        d.get("provider_id", 1),
        d.get("title", "Node"),
        d.get("role", "sub"),
        d.get("x", 100),
        d.get("y", 100)
    )

    return jsonify({
        "ok": True,
        "id": nid
    })


# ==================================================
# MOVE NODE
# ==================================================
@workgroup_bp.route("/node/move", methods=["POST"])
def node_move():
    d = request.get_json(force=True)

    update_node(
        d["id"],
        d["x"],
        d["y"]
    )

    return jsonify({"ok": True})


# ==================================================
# ADD EDGE
# ==================================================
@workgroup_bp.route("/edge/add", methods=["POST"])
def edge_add():
    d = request.get_json(force=True)

    add_edge(
        d["workgroup_id"],
        d["source_id"],
        d["target_id"],
        d.get("relation", "support")
    )

    return jsonify({"ok": True})


# ==================================================
# RUN GRAPH
# ==================================================
@workgroup_bp.route("/workgroup/run", methods=["POST"])
def run_graph():
    d = request.get_json(force=True)

    group_id = int(d["workgroup_id"])
    message = d.get("message", "")

    result = run_group(group_id, message)

    return jsonify(result)
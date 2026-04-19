# services/team_engine.py
# Phase 3 — Full Production Engine
# Drop-in replacement

import json
import time
import uuid
import threading
from queue import Queue
from concurrent.futures import ThreadPoolExecutor, as_completed, TimeoutError
from collections import defaultdict, deque

from core.db import db
from providers.runner import run_model

# ======================================================
# CONFIG
# ======================================================

MAX_WORKERS = 8
MAX_RETRY = 2
NODE_TIMEOUT = 90
MEMORY_LIMIT = 6

VALID_ROLES = {
    "main",
    "sub",
    "advisor",
    "critic",
    "agent",
    "voice",
    "visual"
}

VALID_EDGE_TYPES = {
    "support",
    "delegate",
    "critique",
    "fallback",
    "parallel",
    "memory"
}

# ======================================================
# STREAM BUS
# ======================================================

_streams = {}
_stream_lock = threading.Lock()


def create_stream(run_id):
    with _stream_lock:
        _streams[run_id] = Queue()


def get_stream(run_id):
    with _stream_lock:
        return _streams.get(run_id)


def push_stream(run_id, payload):
    with _stream_lock:
        q = _streams.get(run_id)
        if q:
            q.put(payload)


def close_stream(run_id):
    with _stream_lock:
        q = _streams.get(run_id)
        if q:
            q.put({"type": "done"})
            del _streams[run_id]


def stream_events(run_id):
    q = get_stream(run_id)

    if not q:
        yield 'data: {"type":"missing"}\n\n'
        return

    while True:
        item = q.get()
        yield f"data: {json.dumps(item, ensure_ascii=False)}\n\n"

        if item.get("type") == "done":
            break


# ======================================================
# DB HELPERS
# ======================================================

def ensure_tables():
    with db() as conn:
        conn.execute("""
        CREATE TABLE IF NOT EXISTS node_memory(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            node_id INTEGER,
            text TEXT,
            ts REAL
        )
        """)

        conn.execute("""
        CREATE TABLE IF NOT EXISTS graph_runs(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id TEXT,
            group_id INTEGER,
            message TEXT,
            reply TEXT,
            status TEXT,
            created_at REAL
        )
        """)


def save_run(run_id, group_id, message, reply, status="done"):
    with db() as conn:
        conn.execute("""
        INSERT INTO graph_runs(run_id,group_id,message,reply,status,created_at)
        VALUES(?,?,?,?,?,?)
        """, (run_id, group_id, message[:4000], reply[:8000], status, time.time()))


# ======================================================
# GRAPH LOAD
# ======================================================

def load_graph(group_id):
    with db() as conn:
        nodes = conn.execute(
            "SELECT * FROM nodes WHERE group_id=? ORDER BY id",
            (group_id,)
        ).fetchall()

        edges = conn.execute(
            "SELECT * FROM edges WHERE group_id=? ORDER BY id",
            (group_id,)
        ).fetchall()

    return [dict(x) for x in nodes], [dict(x) for x in edges]


# ======================================================
# MEMORY
# ======================================================

def load_node_memory(node_id, limit=MEMORY_LIMIT):
    with db() as conn:
        rows = conn.execute("""
        SELECT text FROM node_memory
        WHERE node_id=?
        ORDER BY id DESC
        LIMIT ?
        """, (node_id, limit)).fetchall()

    rows = rows[::-1]
    return "\n".join(r["text"] for r in rows)


def save_node_memory(node_id, text):
    if not text:
        return

    with db() as conn:
        conn.execute("""
        INSERT INTO node_memory(node_id,text,ts)
        VALUES(?,?,?)
        """, (node_id, text[:4000], time.time()))


# ======================================================
# GRAPH VALIDATION
# ======================================================

def build_graph(nodes, edges):
    by_id = {n["id"]: n for n in nodes}
    outs = defaultdict(list)
    incoming = defaultdict(list)
    indeg = defaultdict(int)

    for e in edges:
        if e["edge_type"] not in VALID_EDGE_TYPES:
            continue

        s = e["source_id"]
        t = e["target_id"]

        if s not in by_id or t not in by_id:
            continue

        outs[s].append(e)
        incoming[t].append(e)
        indeg[t] += 1

    for n in nodes:
        indeg[n["id"]] = indeg.get(n["id"], 0)

    return by_id, outs, incoming, indeg


def detect_cycle(nodes, edges):
    by_id, outs, _, indeg = build_graph(nodes, edges)

    q = deque([nid for nid in by_id if indeg[nid] == 0])
    seen = 0

    while q:
        cur = q.popleft()
        seen += 1

        for e in outs[cur]:
            nxt = e["target_id"]
            indeg[nxt] -= 1
            if indeg[nxt] == 0:
                q.append(nxt)

    return seen != len(by_id)


# ======================================================
# PROMPT BUILDER
# ======================================================

def join_text(items):
    return "\n".join(x for x in items if x)


def build_prompt(node, message, outputs, incoming_edges):
    support = []
    critiques = []
    fallback = []
    delegated = []

    for e in incoming_edges:
        src = str(e["source_id"])
        txt = outputs.get(src, "")
        if not txt:
            continue

        tp = e["edge_type"]

        if tp in ("support", "parallel"):
            support.append(txt)

        elif tp == "critique":
            critiques.append(txt)

        elif tp == "fallback":
            fallback.append(txt)

        elif tp == "delegate":
            delegated.append(txt)

    memory = load_node_memory(node["id"])
    system_prompt = node.get("system_prompt", "") or ""

    prompt = f"""
{system_prompt}

You are AI Node: {node['label']}
Role: {node['node_role']}

USER TASK:
{message}

MEMORY:
{memory}

SUPPORT:
{join_text(support)}

DELEGATED RESULTS:
{join_text(delegated)}

CRITIQUE:
{join_text(critiques)}

FALLBACK:
{join_text(fallback)}

Return only your response.
""".strip()

    return prompt


# ======================================================
# NODE EXECUTION
# ======================================================

def execute_node(node, message, outputs, incoming_edges, run_id):
    role = node["node_role"]

    if role not in VALID_ROLES:
        return {
            "node": node["label"],
            "role": role,
            "status": "skipped",
            "output": "[invalid role]"
        }

    model_id = node.get("model_id")
    if not model_id:
        return {
            "node": node["label"],
            "role": role,
            "status": "skipped",
            "output": ""
        }

    prompt = build_prompt(node, message, outputs, incoming_edges)
    last_err = None

    for attempt in range(1, MAX_RETRY + 2):
        try:
            push_stream(run_id, {
                "type": "node_start",
                "node": node["label"],
                "attempt": attempt
            })

            out = run_model(model_id, prompt)

            save_node_memory(node["id"], out)

            push_stream(run_id, {
                "type": "node_done",
                "node": node["label"],
                "output": out
            })

            return {
                "node": node["label"],
                "role": role,
                "status": "done",
                "output": out
            }

        except Exception as e:
            last_err = str(e)

            push_stream(run_id, {
                "type": "node_error",
                "node": node["label"],
                "attempt": attempt,
                "error": last_err
            })

    return {
        "node": node["label"],
        "role": role,
        "status": "error",
        "output": f"[ERROR] {last_err}"
    }


# ======================================================
# MAIN RUNTIME
# ======================================================

def run_group(group_id, message, run_id=None):
    ensure_tables()

    if run_id is None:
        run_id = uuid.uuid4().hex

    create_stream(run_id)

    nodes, edges = load_graph(group_id)

    if not nodes:
        close_stream(run_id)
        return {
            "run_id": run_id,
            "reply": "No nodes configured.",
            "logs": []
        }

    if detect_cycle(nodes, edges):
        close_stream(run_id)
        return {
            "run_id": run_id,
            "reply": "Graph contains cycle.",
            "logs": []
        }

    by_id, outs, incoming, indeg = build_graph(nodes, edges)

    ready = [nid for nid, d in indeg.items() if d == 0]
    outputs = {}
    logs = []

    started = time.time()

    try:
        while ready:
            batch = ready[:]
            ready = []

            futures = {}

            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
                for nid in batch:
                    node = by_id[nid]

                    fut = pool.submit(
                        execute_node,
                        node,
                        message,
                        outputs.copy(),
                        incoming[nid],
                        run_id
                    )
                    futures[fut] = nid

                for fut in as_completed(futures):
                    nid = futures[fut]

                    try:
                        result = fut.result(timeout=NODE_TIMEOUT)

                    except TimeoutError:
                        result = {
                            "node": by_id[nid]["label"],
                            "role": by_id[nid]["node_role"],
                            "status": "timeout",
                            "output": "[TIMEOUT]"
                        }

                    except Exception as e:
                        result = {
                            "node": by_id[nid]["label"],
                            "role": by_id[nid]["node_role"],
                            "status": "error",
                            "output": str(e)
                        }

                    logs.append(result)
                    outputs[str(nid)] = result["output"]

                    for e in outs[nid]:
                        nxt = e["target_id"]
                        indeg[nxt] -= 1
                        if indeg[nxt] == 0:
                            ready.append(nxt)

        # prefer main nodes
        main_replies = [
            x["output"] for x in logs
            if x["role"] == "main" and x["output"]
        ]

        if main_replies:
            final = "\n\n".join(main_replies)
        elif logs:
            final = logs[-1]["output"]
        else:
            final = ""

        took = round(time.time() - started, 2)

        push_stream(run_id, {
            "type": "final",
            "reply": final,
            "seconds": took
        })

        save_run(run_id, group_id, message, final, "done")

        return {
            "run_id": run_id,
            "reply": final,
            "logs": logs,
            "seconds": took
        }

    finally:
        close_stream(run_id)


# ======================================================
# OLD API COMPATIBILITY
# ======================================================

def _find_default_group(cfg):
    try:
        gid = cfg.get("group_id")
        if gid:
            return int(gid)
    except:
        pass
    return 1


def run_private_with_support(message, cfg):
    gid = _find_default_group(cfg)
    r = run_group(gid, message)
    return r["reply"], "graph-engine"


def run_team_chat(message, cfg):
    gid = _find_default_group(cfg)
    r = run_group(gid, message)

    msgs = []
    for item in r["logs"]:
        msgs.append({
            "sender": item["node"],
            "role": item["role"],
            "text": item["output"],
            "status": item["status"]
        })

    return msgs
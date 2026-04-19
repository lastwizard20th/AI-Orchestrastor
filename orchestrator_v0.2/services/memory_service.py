import os, time, json, math, sqlite3, threading
from queue import Queue
from sentence_transformers import SentenceTransformer
from config import EMBED_MODEL

DB='data/memory.db'
os.makedirs('data', exist_ok=True)
_model=None
_lock=threading.Lock()
queue=Queue()


def conn():
    c=sqlite3.connect(DB, check_same_thread=False)
    c.row_factory=sqlite3.Row
    c.execute('''CREATE TABLE IF NOT EXISTS memories(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ts REAL,
        text TEXT,
        embedding TEXT
    )''')
    return c

def embedder():
    global _model
    if _model is None:
        with _lock:
            if _model is None:
                _model = SentenceTransformer(EMBED_MODEL)
    return _model


def cosine(a,b):
    dot=sum(x*y for x,y in zip(a,b))
    na=math.sqrt(sum(x*x for x in a))
    nb=math.sqrt(sum(x*x for x in b))
    return dot/(na*nb+1e-9)

def save_memory(text):
    text=text.strip()
    if len(text)<4:
        return
    vec = embedder().encode(text).tolist()
    c=conn()
    c.execute('INSERT INTO memories(ts,text,embedding) VALUES(?,?,?)',
              (time.time(), text, json.dumps(vec)))
    c.commit(); c.close()


def worker():
    while True:
        item=queue.get()
        try:
            save_memory(item)
        finally:
            queue.task_done()

threading.Thread(target=worker, daemon=True).start()


def save_memory_async(text):
    queue.put(text)

def search_memory(query, top_k=3):
    if not query.strip():
        return ''
    qv=embedder().encode(query).tolist()
    c=conn()
    rows=c.execute('SELECT text,embedding FROM memories ORDER BY id DESC LIMIT 500').fetchall()
    c.close()
    scored=[]
    for r in rows:
        try:
            score=cosine(qv, json.loads(r['embedding']))
            if score>0.2:
                scored.append((score,r['text']))
        except:
            pass
    scored.sort(reverse=True)
    return ''.join(x[1] for x in scored[:top_k])

def get_all_memories(limit=200):
    c=conn(); rows=c.execute('SELECT id,text,ts FROM memories ORDER BY id DESC LIMIT ?', (limit,)).fetchall(); c.close()
    return [dict(r) for r in rows]


def delete_memory(mem_id):
    c=conn(); c.execute('DELETE FROM memories WHERE id=?',(mem_id,)); c.commit(); c.close()
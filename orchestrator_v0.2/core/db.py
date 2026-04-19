import os, sqlite3, threading
from contextlib import contextmanager

DATA_DIR='data'
DB_PATH=os.path.join(DATA_DIR,'main.db')
os.makedirs(DATA_DIR, exist_ok=True)
_lock=threading.Lock()

SCHEMA='''
CREATE TABLE IF NOT EXISTS providers(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT UNIQUE NOT NULL,
 kind TEXT NOT NULL,
 base_url TEXT DEFAULT '',
 api_key TEXT DEFAULT '',
 enabled INTEGER DEFAULT 1,
 created_at REAL DEFAULT (strftime('%s','now'))
);
CREATE TABLE IF NOT EXISTS models(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 provider_id INTEGER NOT NULL,
 name TEXT NOT NULL,
 role TEXT DEFAULT 'core',
 temperature REAL DEFAULT 0.4,
 max_tokens INTEGER DEFAULT 2048,
 system_prompt TEXT DEFAULT '',
 personality TEXT DEFAULT '',
 enabled INTEGER DEFAULT 1,
 FOREIGN KEY(provider_id) REFERENCES providers(id) ON DELETE CASCADE
);
CREATE TABLE IF NOT EXISTS workgroups(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT UNIQUE NOT NULL,
 config TEXT DEFAULT '{}',
 created_at REAL DEFAULT (strftime('%s','now'))
);
CREATE TABLE IF NOT EXISTS nodes(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 group_id INTEGER NOT NULL,
 model_id INTEGER,
 label TEXT NOT NULL,
 node_role TEXT NOT NULL,
 pos_x REAL DEFAULT 0,
 pos_y REAL DEFAULT 0,
 config TEXT DEFAULT '{}',
 FOREIGN KEY(group_id) REFERENCES workgroups(id) ON DELETE CASCADE,
 FOREIGN KEY(model_id) REFERENCES models(id) ON DELETE SET NULL
);
CREATE TABLE IF NOT EXISTS edges(
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 group_id INTEGER NOT NULL,
 source_id INTEGER NOT NULL,
 target_id INTEGER NOT NULL,
 edge_type TEXT DEFAULT 'support',
 FOREIGN KEY(group_id) REFERENCES workgroups(id) ON DELETE CASCADE
);
'''
def get_conn():
 c=sqlite3.connect(DB_PATH, check_same_thread=False)
 c.row_factory=sqlite3.Row
 c.execute('PRAGMA foreign_keys=ON;')
 c.execute('PRAGMA journal_mode=WAL;')
 return c

@contextmanager
def db():
 c=get_conn()
 try:
  yield c
  c.commit()
 finally:
  c.close()

def init_db():
 with _lock:
  with db() as c:
   c.executescript(SCHEMA)
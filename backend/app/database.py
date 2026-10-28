import json, sqlite3
from datetime import datetime, timezone
from .config import DB_PATH

def connect():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    with connect() as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS analyses (id INTEGER PRIMARY KEY AUTOINCREMENT, kind TEXT NOT NULL, title TEXT NOT NULL, summary TEXT NOT NULL, result_json TEXT NOT NULL, created_at TEXT NOT NULL)")
        conn.commit()

def save_analysis(kind, title, summary, result):
    created = datetime.now(timezone.utc).isoformat()
    with connect() as conn:
        cur = conn.execute("INSERT INTO analyses(kind,title,summary,result_json,created_at) VALUES(?,?,?,?,?)",
                           (kind, title, summary, json.dumps(result), created))
        conn.commit()
        return {"id": cur.lastrowid, "kind": kind, "title": title, "summary": summary, "result": result, "created_at": created}

def list_analyses(limit=50):
    with connect() as conn:
        rows = conn.execute("SELECT * FROM analyses ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
    return [{"id":r["id"],"kind":r["kind"],"title":r["title"],"summary":r["summary"],
             "result":json.loads(r["result_json"]),"created_at":r["created_at"]} for r in rows]

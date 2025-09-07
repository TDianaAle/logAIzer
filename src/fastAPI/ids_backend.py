from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import datetime

DB_PATH = "ids_demo.db"
app = FastAPI(title="IDS Demo Backend")

# Init DB
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Ottieni le colonne attuali della tabella (se esiste)
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
    table_exists = c.fetchone() is not None

    expected_columns = {
        "id", "ip", "protocol", "service", "flag", "src_bytes", "dst_bytes", "prediction", "timestamp"
    }

    recreate = False
    if table_exists:
        c.execute("PRAGMA table_info(events)")
        existing_columns = {row[1] for row in c.fetchall()}

        # Se mancano colonne → ricrea tabella
        if not expected_columns.issubset(existing_columns):
            recreate = True
    else:
        recreate = True

    if recreate:
        print("🔄 Ricreo tabella events con schema aggiornato...")
        c.execute("DROP TABLE IF EXISTS events")
        c.execute("""
        CREATE TABLE events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            protocol TEXT,
            service TEXT,
            flag TEXT,
            src_bytes INTEGER,
            dst_bytes INTEGER,
            prediction TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

    conn.commit()
    conn.close()

init_db()

# Schema input
class PredictRequest(BaseModel):
    ip: str
    protocol: str
    service: str
    flag: str
    src_bytes: int
    dst_bytes: int

@app.post("/predict")
def predict(req: PredictRequest):
    prediction = "normal"
    details = "Legit traffic"

    # 🔎 euristiche IDS (semplici per demo)
    if req.flag.upper() == "SYN" and req.src_bytes == 0 and req.dst_bytes == 0:
        prediction = "attack"
        details = "Possible SYN flood (SYN packets without payload)"
    elif req.src_bytes > 1000:
        prediction = "attack"
        details = "Possible brute force / abnormal traffic (high outbound bytes)"
    elif req.protocol.lower() == "udp" and req.dst_bytes == 0:
        prediction = "attack"
        details = "Possible network probe (UDP packets with no response)"
    elif req.protocol.lower() == "icmp":
        prediction = "attack"
        details = "Possible ping sweep (ICMP traffic detected)"

    # salva in DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO events (ip, protocol, service, flag, src_bytes, dst_bytes, prediction)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (req.ip, req.protocol, req.service, req.flag, req.src_bytes, req.dst_bytes, prediction))
    conn.commit()
    conn.close()

    return {"ip": req.ip, "prediction": prediction, "details": details}

@app.get("/logs")
def get_logs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT timestamp, ip, prediction, details FROM events ORDER BY timestamp DESC")
    rows = c.fetchall()
    conn.close()
    return [{"timestamp": r[0], "ip": r[1], "prediction": r[2], "details": r[3]} for r in rows]

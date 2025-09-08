from fastapi import FastAPI
from pydantic import BaseModel
import sqlite3
import torch
import pandas as pd
import os
import joblib

# === Config ===
DB_PATH = "ids_demo.db"
MODEL_PATH = "./reports/model_best.pth"
FEATURES_FILE = "./reports/feature_importance.csv"
ENCODERS_PATH = "./reports/encoders.joblib"
SCALER_PATH = "./reports/scaler.joblib"
TOP_K = 8
DEVICE = "cpu"

# === Import modello ===
from ..torch_models import MLPClassifier

# Carica top-k feature dall’EDA
feat_df = pd.read_csv(FEATURES_FILE)
SELECTED_FEATURES = feat_df.head(TOP_K)["feature"].tolist()

# Carica modello
model = MLPClassifier(input_dim=TOP_K).to(DEVICE)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.eval()

app = FastAPI(title="IDS Backend (MLPClassifier)")

# === DB Init ===
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    expected_columns = {
        "id", "ip", "protocol", "service", "flag",
        "src_bytes", "dst_bytes",
        "same_srv_rate", "dst_host_srv_count",
        "dst_host_same_srv_rate", "logged_in",
        "diff_srv_rate",
        "prediction", "details", "timestamp"
    }
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='events'")
    table_exists = c.fetchone() is not None

    recreate = False
    if table_exists:
        c.execute("PRAGMA table_info(events)")
        existing_columns = {row[1] for row in c.fetchall()}
        if not expected_columns.issubset(existing_columns):
            recreate = True
    else:
        recreate = True

    if recreate:
        print(" Ricrea tabella events con schema aggiornato...")
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
            same_srv_rate REAL,
            dst_host_srv_count INTEGER,
            dst_host_same_srv_rate REAL,
            logged_in INTEGER,
            diff_srv_rate REAL,
            prediction TEXT,
            details TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
    conn.commit()
    conn.close()

init_db()

# === Schema input ===
class PredictRequest(BaseModel):
    ip: str
    protocol: str
    service: str
    flag: str
    src_bytes: int
    dst_bytes: int
    same_srv_rate: float
    dst_host_srv_count: int
    dst_host_same_srv_rate: float
    logged_in: int
    diff_srv_rate: float

# === Preprocessing ===
def preprocess(req: PredictRequest):
    from ..dataloader import preprocess_sample

    # Crea un dizionario con tutte le feature richieste
    sample = {
        "protocol_type": req.protocol,
        "service": req.service,
        "flag": req.flag,
        "src_bytes": req.src_bytes,
        "dst_bytes": req.dst_bytes,
        "same_srv_rate": req.same_srv_rate,
        "dst_host_srv_count": req.dst_host_srv_count,
        "dst_host_same_srv_rate": req.dst_host_same_srv_rate,
        "logged_in": req.logged_in,
        "diff_srv_rate": req.diff_srv_rate,
    }

    # Assicura che tutte le feature attese dal modello siano presenti
    for feat in SELECTED_FEATURES:
        if feat not in sample:
            sample[feat] = 0

    # Gestione valori categorici non visti
    encoders = joblib.load(ENCODERS_PATH)
    for col in ["protocol_type", "service", "flag"]:
        if col in sample and col in encoders:
            known_classes = set(encoders[col].classes_)
            if sample[col] not in known_classes:
                print(f"[WARN] valore sconosciuto '{sample[col]}' in colonna {col}, sostituito con '{encoders[col].classes_[0]}'")
                sample[col] = encoders[col].classes_[0]

    # Preprocess finale
    X = preprocess_sample(
        sample,
        encoder_path=ENCODERS_PATH,
        scaler_path=SCALER_PATH,
        features=SELECTED_FEATURES
    )
    return X

# === Endpoint predict ===
@app.post("/predict")
def predict(req: PredictRequest):
    x = preprocess(req)
    x_tensor = torch.tensor(x, dtype=torch.float32).to(DEVICE)

    with torch.no_grad():
        y_pred = model(x_tensor).argmax(dim=1).item()

    prediction = "attack" if y_pred == 1 else "normal"
    details = "Predizione con modello ML (MLPClassifier)"

    # salva in DB
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        INSERT INTO events (
            ip, protocol, service, flag,
            src_bytes, dst_bytes, same_srv_rate,
            dst_host_srv_count, dst_host_same_srv_rate,
            logged_in, diff_srv_rate,
            prediction, details
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        req.ip, req.protocol, req.service, req.flag,
        req.src_bytes, req.dst_bytes, req.same_srv_rate,
        req.dst_host_srv_count, req.dst_host_same_srv_rate,
        req.logged_in, req.diff_srv_rate,
        prediction, details
    ))
    conn.commit()
    conn.close()

    return {"ip": req.ip, "prediction": prediction, "details": details}

# === Endpoint logs ===
@app.get("/logs")
def get_logs():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT timestamp, ip, prediction, details
        FROM events ORDER BY timestamp DESC
    """)
    rows = c.fetchall()
    conn.close()
    return [
        {"timestamp": r[0], "ip": r[1], "prediction": r[2], "details": r[3]}
        for r in rows
    ]

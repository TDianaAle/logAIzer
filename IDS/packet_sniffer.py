import time
import csv
import joblib
import pandas as pd
from collections import defaultdict, deque
from scapy.all import sniff, TCP, IP, UDP

# === Parametri ===
MODEL_PATH = "./reports/random_forest_model.joblib"
SCALER_PATH = "./reports/scaler.joblib"
ENCODERS_PATH = "./reports/encoders.joblib"
CSV_PATH = "./reports/captured_packets.csv"
INTERFACE = None     # None = interfaccia di default
DURATION = 60        # secondi di cattura
WINDOW_SIZE = 500    # pacchetti recenti per feature aggregate

# === Caricamento modello e preprocessing ===
print("[INFO] Caricamento modello e preprocessing...")
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)
encoders = joblib.load(ENCODERS_PATH)

# === Lista feature nell'ordine corretto ===
FEATURES = [
    "src_bytes","dst_bytes","same_srv_rate","dst_host_srv_count",
    "dst_host_same_srv_rate","flag","logged_in","diff_srv_rate",
    "protocol_type","count","srv_serror_rate","dst_host_diff_srv_rate",
    "service","dst_host_same_src_port_rate","serror_rate",
    "dst_host_srv_diff_host_rate","srv_count","dst_host_rerror_rate",
    "dst_host_count","dst_host_serror_rate"
]

# === Stato per feature aggregate ===
connection_stats = defaultdict(lambda: {"src_bytes":0, "dst_bytes":0})
recent_packets = deque(maxlen=WINDOW_SIZE)

# === Mapping TCP flags ( trasforma flag di Scapy nelle categorie del dataset NSL-KDD) ===
FLAG_MAPPING = {
    "S": "S0", "SA": "S1",
    "A": "SF", "PA": "SF", "FA": "SF",
    "R": "REJ", "RA": "RSTR",
    "FPA": "SF", "": "SF"
}

# === Funzione per calcolare feature ===
def extract_features(pkt):
    try:
        src = pkt[IP].src
        dst = pkt[IP].dst
        sport = pkt.sport
        dport = pkt.dport
        length = len(pkt)

        conn_key = (src, dst, sport, dport)
        connection_stats[conn_key]["src_bytes"] += length
        connection_stats[conn_key]["dst_bytes"] += 0  # semplificazione

        if pkt.haslayer(TCP):
            raw_flag = str(pkt[TCP].flags)
            mapped_flag = FLAG_MAPPING.get(raw_flag, "SF")
            proto = "tcp"
        else:
            mapped_flag = "SF"  # default per UDP
            proto = "udp"

        recent_packets.append({
            "src": src, "dst": dst, "sport": sport, "dport": dport,
            "len": length, "proto": proto, "flag": mapped_flag
        })

        features = {
            "src_bytes": connection_stats[conn_key]["src_bytes"],
            "dst_bytes": connection_stats[conn_key]["dst_bytes"],
            "same_srv_rate": sum(1 for p in recent_packets if p["dport"]==dport)/len(recent_packets),
            "dst_host_srv_count": sum(1 for p in recent_packets if p["dst"]==dst and p["dport"]==dport),
            "dst_host_same_srv_rate": sum(1 for p in recent_packets if p["dst"]==dst and p["dport"]==dport)/max(1,sum(1 for p in recent_packets if p["dst"]==dst)),
            "flag": mapped_flag,
            "logged_in": 0,
            "diff_srv_rate": sum(1 for p in recent_packets if p["dport"]!=dport)/len(recent_packets),
            "protocol_type": proto,
            "count": len([p for p in recent_packets if p["src"]==src]),
            "srv_serror_rate": 0.0,
            "dst_host_diff_srv_rate": sum(1 for p in recent_packets if p["dst"]==dst and p["dport"]!=dport)/max(1,sum(1 for p in recent_packets if p["dst"]==dst)),
            "service": str(dport),
            "dst_host_same_src_port_rate": sum(1 for p in recent_packets if p["dst"]==dst and p["sport"]==sport)/max(1,sum(1 for p in recent_packets if p["dst"]==dst)),
            "serror_rate": 0.0,
            "dst_host_srv_diff_host_rate": sum(1 for p in recent_packets if p["dport"]==dport and p["dst"]!=dst)/max(1,sum(1 for p in recent_packets if p["dport"]==dport)),
            "srv_count": sum(1 for p in recent_packets if p["dport"]==dport),
            "dst_host_rerror_rate": 0.0,
            "dst_host_count": sum(1 for p in recent_packets if p["dst"]==dst),
            "dst_host_serror_rate": 0.0
        }

        return features, src, dst, sport, dport

    except Exception:
        return None, None, None, None, None

# === Preprocessing feature vector ===
def preprocess(features):
    row = []
    for f in FEATURES:
        val = features[f]
        if f in ["protocol_type", "service", "flag"]:
            enc = encoders[f]
            if hasattr(enc, "transform"):
                try:
                    val = enc.transform([val])[0]
                except ValueError:
                    val = -1
            elif isinstance(enc, dict):
                val = enc.get(val, -1)
        row.append(val)

    row_df = pd.DataFrame([row], columns=FEATURES)
    row_scaled = scaler.transform(row_df)
    return row_scaled, row_df.iloc[0].to_dict()

# === Callback sniffer ===
def process_packet(pkt):
    if not pkt.haslayer(IP):
        return

    features, src, dst, sport, dport = extract_features(pkt)
    if features is None:
        return

    try:
        feat_vector, feat_dict = preprocess(features)
        prediction = model.predict(feat_vector)[0]
        prob = model.predict_proba(feat_vector)[0][1]
        label = "normal" if prediction == 0 else "possibile attacco rilevato"

        # regola euristica extra per flood
        if feat_dict["srv_count"] > 50 or feat_dict["count"] > 100:
            label = "possibile attacco rilevato (euristica)"

        print(f"[{time.strftime('%H:%M:%S')}] {src}:{sport} -> {dst}:{dport} | {label} | prob={prob:.2f}")

        with open(CSV_PATH, "a", newline="") as f:
            writer = csv.writer(f)
            row = [time.strftime("%Y-%m-%d %H:%M:%S"), src, dst, sport, dport]
            row.extend([feat_dict[f] for f in FEATURES])
            row.append(label)
            writer.writerow(row)

    except Exception as e:
        print(f"[ERRORE] {e}")

# === Main ===
def main():
    with open(CSV_PATH, "w", newline="") as f:
        writer = csv.writer(f)
        header = ["timestamp","src","dst","sport","dport"] + FEATURES + ["prediction"]
        writer.writerow(header)

    print(f"[INFO] Avvio sniffer per {DURATION} secondi...")
    sniff(prn=process_packet, filter="tcp or udp", iface=INTERFACE, timeout=DURATION)
    print(f"[INFO] Sniffing terminato. Report in {CSV_PATH}")

if __name__ == "__main__":
    main()

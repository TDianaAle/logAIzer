# IDS/feature_extractor.py
# poiché è necessario replicare i gruppi principali (Basic + Traffic)
#  che bastano per la dimostrazione

import time
from collections import defaultdict

# Stato per mantenere statistiche sul traffico
traffic_window = []
window_size = 2 #secondi come nel dataset
stats = defaultdict(list)

def extract_features(pkt):
    """
    Estrae un sottoinsieme delle feature NSL-KDD da un pacchetto scapy.
    Restituisce un dizionario compatibile con il modello ML.
    """
    global traffic_window

    features = {}

    # Timestamp pacchetto
    ts = time.time()

    # ------------------------------
    # Basic features
    # ------------------------------
    features["duration"] = 0  # durata singolo pacchetto (non connessione)
    features["protocol_type"] = pkt.payload.name.lower() if hasattr(pkt, "payload") else "other"
    features["service"] = pkt.sport if hasattr(pkt, "sport") else 0
    features["flag"] = 0  # placeholder: flag TCP richiederebbe parsing handshake
    features["src_bytes"] = len(pkt.original) if hasattr(pkt, "original") else 0
    features["dst_bytes"] = len(pkt.payload) if hasattr(pkt, "payload") else 0

    # ------------------------------
    # Traffic features (finestra temporale)
    # ------------------------------
    # Mantiene pacchetti recenti nella finestra di 2 secondi
    traffic_window = [p for p in traffic_window if ts - p["time"] <= window_size]
    traffic_window.append({"time": ts, "sport": features["service"]})

    total_conns = len(traffic_window)
    same_srv = len([p for p in traffic_window if p["sport"] == features["service"]])

    features["count"] = total_conns
    features["srv_count"] = same_srv
    features["same_srv_rate"] = same_srv / total_conns if total_conns > 0 else 0
    features["diff_srv_rate"] = 1 - features["same_srv_rate"] if total_conns > 0 else 0

    return features

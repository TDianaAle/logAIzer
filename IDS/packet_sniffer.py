

import scapy.all as scapy
import pandas as pd
import joblib
import time

# === Percorsi ai file salvati ===
MODEL_PATH = "./reports/random_forest_model.joblib"
SCALER_PATH = "./reports/scaler.joblib"
FEATURES_FILE = "./reports/feature_importance.csv"

# === Caricamento modello e scaler ===
model = joblib.load(MODEL_PATH)
scaler = joblib.load(SCALER_PATH)

# === Costruzione DataFrame con feature attese ===
def build_feature_dataframe(packet_features: dict):
    """
    Costruisce un DataFrame con tutte le feature attese dal modello.
    Riempie con 0 quelle non disponibili dallo sniffer.
    """
    feat_df = pd.read_csv(FEATURES_FILE)
    selected_features = feat_df.head(20)["feature"].tolist()

    # inizializza tutte le feature a 0
    complete_features = {f: 0 for f in selected_features}

    # aggiorna con i valori raccolti dal pacchetto
    for k, v in packet_features.items():
        if k in complete_features:
            complete_features[k] = v

    return pd.DataFrame([complete_features])


# === Funzione di analisi pacchetto ===
def process_packet(packet):
    try:
        # estrae alcune feature di base dal pacchetto
        packet_features = {
            "src_bytes": len(packet.payload) if hasattr(packet, "payload") else 0,
            "dst_bytes": len(packet) - len(packet.payload) if hasattr(packet, "payload") else len(packet),
            "protocol_type": packet.proto if hasattr(packet, "proto") else 0,
            "service": packet.dport if hasattr(packet, "dport") else 0,
            "flag": 1, 
            "count": 1,
            "srv_count": 1,
            "same_srv_rate": 0.0,
            "diff_srv_rate": 0.0,
        }

        # costruisce dataframe completo
        df = build_feature_dataframe(packet_features)

        # scaling
        X = scaler.transform(df)

        # predizione
        prediction = model.predict(X)[0]

        if prediction == 1:
            print("[ALERT]  Intrusione rilevata!")
        else:
            print("[OK]  Traffico normale")

    except Exception as e:
        print(f"[ERRORE] durante process_packet: {e}")


# === MAIN ===
if __name__ == "__main__":
    print("[INFO] Avvio sniffer per 120 secondi sulla porta 5173...")

    packets = scapy.sniff(
        iface="\\Device\\NPF_Loopback", 
        filter="tcp port 5173",
        prn=process_packet,
        timeout=120
    )

    print("[INFO] Sniffing terminato.")

# src/inference.py

import joblib
import pandas as pd
from dataloader import DataLoader

def load_model(model_path):
    """Carica un modello salvato"""
    model = joblib.load(model_path)
    print(f"[INFO] Modello caricato da {model_path}")
    return model

def predict_instance(model, instance):
    """
    Predice la classe di una singola istanza (dizionario di feature).
    Esempio instance:
    {
        "duration": 0, "protocol_type": "tcp", "service": "http", ...
    }
    """
    # Creiamo un DataFrame con una sola riga
    df = pd.DataFrame([instance])
    dl = DataLoader(None, None)  # DataLoader per preprocessing
    X, _ = dl.preprocess(df, binary=True)
    prediction = model.predict(X)[0]
    return "attack" if prediction == 1 else "normal"

if __name__ == "__main__":
    # Esempio di utilizzo
    model = load_model("reports/random_forest_model.joblib")
    
    example_instance = {
        "duration": 0, "protocol_type": "tcp", "service": "http", "flag": "SF",
        "src_bytes": 181, "dst_bytes": 5450, "land": 0, "wrong_fragment": 0,
        "urgent": 0, "hot": 0, "num_failed_logins": 0, "logged_in": 1,
        "num_compromised": 0, "root_shell": 0, "su_attempted": 0,
        "num_root": 0, "num_file_creations": 0, "num_shells": 0,
        "num_access_files": 0, "num_outbound_cmds": 0, "is_host_login": 0,
        "is_guest_login": 0, "count": 2, "srv_count": 2, "serror_rate": 0.0,
        "srv_serror_rate": 0.0, "rerror_rate": 0.0, "srv_rerror_rate": 0.0,
        "same_srv_rate": 1.0, "diff_srv_rate": 0.0, "srv_diff_host_rate": 0.0,
        "dst_host_count": 150, "dst_host_srv_count": 25, "dst_host_same_srv_rate": 0.17,
        "dst_host_diff_srv_rate": 0.03, "dst_host_same_src_port_rate": 0.0,
        "dst_host_srv_diff_host_rate": 0.0, "dst_host_serror_rate": 0.0,
        "dst_host_srv_serror_rate": 0.0, "dst_host_rerror_rate": 0.05,
        "dst_host_srv_rerror_rate": 0.0, "label": "normal", "difficulty": 1
    }

    prediction = predict_instance(model, example_instance)
    print(f"Prediction: {prediction}")

# src/inference_torch.py

import torch
import torch.nn as nn
import joblib
import pandas as pd
import numpy as np

from torch_models import MLPClassifier
from dataloader import preprocess_sample

# Config
MODEL_PATH = "./reports/model_best.pth"
FEATURES_FILE = "./reports/feature_importance.csv"
TOP_K = 20

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Carica le feature selezionate
features = pd.read_csv(FEATURES_FILE).head(TOP_K)["feature"].tolist()

# Carica modello
input_dim = len(features)
model = MLPClassifier(input_dim=input_dim)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.to(DEVICE)
model.eval()

print("[INFO] Modello caricato correttamente.")

def predict(sample: dict):
    """
    sample: dizionario con le stesse chiavi del dataset NSL-KDD
    Esempio:
    {
        "duration": 0,
        "protocol_type": "tcp",
        "service": "http",
        "flag": "SF",
        "src_bytes": 181,
        "dst_bytes": 5450,
        ...
    }
    """
    # Preprocessing (usa lo stesso scaler/encoder salvato)
    X = preprocess_sample(sample, features=features)
    X_tensor = torch.tensor(X, dtype=torch.float32).to(DEVICE)

    with torch.no_grad():
        outputs = model(X_tensor)
        _, predicted = torch.max(outputs, 1)

    label = int(predicted.item())
    return "normal" if label == 0 else "attack"


if __name__ == "__main__":
    # Esempiodi un campione normale
    sample_normal = {
        "duration": 0, "protocol_type": "tcp", "service": "http", "flag": "SF",
        "src_bytes": 181, "dst_bytes": 5450, "land": 0, "wrong_fragment": 0, "urgent": 0,
        "hot": 0, "num_failed_logins": 0, "logged_in": 1, "num_compromised": 0,
        "root_shell": 0, "su_attempted": 0, "num_root": 0, "num_file_creations": 0,
        "num_shells": 0, "num_access_files": 0, "num_outbound_cmds": 0,
        "is_host_login": 0, "is_guest_login": 0, "count": 9, "srv_count": 9,
        "serror_rate": 0.00, "srv_serror_rate": 0.00, "rerror_rate": 0.00,
        "srv_rerror_rate": 0.00, "same_srv_rate": 1.00, "diff_srv_rate": 0.00,
        "srv_diff_host_rate": 0.00, "dst_host_count": 9, "dst_host_srv_count": 9,
        "dst_host_same_srv_rate": 1.00, "dst_host_diff_srv_rate": 0.00,
        "dst_host_same_src_port_rate": 0.11, "dst_host_srv_diff_host_rate": 0.00,
        "dst_host_serror_rate": 0.00, "dst_host_srv_serror_rate": 0.00,
        "dst_host_rerror_rate": 0.00, "dst_host_srv_rerror_rate": 0.00
    }

    print("Predizione:", predict(sample_normal))
# src/inference_torch.py

import torch
import pandas as pd
from torch_models import MLPClassifier
from dataloader import preprocess_sample

# Config
MODEL_PATH = "./reports/model_best.pth"
FEATURES_FILE = "./reports/feature_importance.csv"
TOP_K = 20

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Carica le top-K feature da usare
features = pd.read_csv(FEATURES_FILE).head(TOP_K)["feature"].tolist()

# Inizializza modello
input_dim = len(features)
model = MLPClassifier(input_dim=input_dim)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.to(DEVICE)
model.eval()

print("[INFO] Modello caricato correttamente.")

def predict(sample: dict):
    """
    sample: dizionario con tutte le 41 feature originali del dataset NSL-KDD.
    """
    # Preprocessing (usa encoder/scaler salvati + riduzione top-K feature)
    X = preprocess_sample(sample, features=features)
    X_tensor = torch.tensor(X, dtype=torch.float32).to(DEVICE)

    with torch.no_grad():
        outputs = model(X_tensor)
        _, predicted = torch.max(outputs, 1)

    label = int(predicted.item())
    return "normal" if label == 0 else "attack"


if __name__ == "__main__":
    # campione con tutte le 41 feature NSL-KDD tranne difficulti e labels
    sample_example = {
        "duration": 0,
        "protocol_type": "tcp",
        "service": "http",
        "flag": "SF",
        "src_bytes": 181,
        "dst_bytes": 5450,
        "land": 0,
        "wrong_fragment": 0,
        "urgent": 0,
        "hot": 0,
        "num_failed_logins": 0,
        "logged_in": 1,
        "num_compromised": 0,
        "root_shell": 0,
        "su_attempted": 0,
        "num_root": 0,
        "num_file_creations": 0,
        "num_shells": 0,
        "num_access_files": 0,
        "num_outbound_cmds": 0,
        "is_host_login": 0,
        "is_guest_login": 0,
        "count": 9,
        "srv_count": 9,
        "serror_rate": 0.00,
        "srv_serror_rate": 0.00,
        "rerror_rate": 0.00,
        "srv_rerror_rate": 0.00,
        "same_srv_rate": 1.00,
        "diff_srv_rate": 0.00,
        "srv_diff_host_rate": 0.00,
        "dst_host_count": 9,
        "dst_host_srv_count": 9,
        "dst_host_same_srv_rate": 1.00,
        "dst_host_diff_srv_rate": 0.00,
        "dst_host_same_src_port_rate": 0.11,
        "dst_host_srv_diff_host_rate": 0.00,
        "dst_host_serror_rate": 0.00,
        "dst_host_srv_serror_rate": 0.00,
        "dst_host_rerror_rate": 0.00,
        "dst_host_srv_rerror_rate": 0.00
    }

    print("Predizione:", predict(sample_example))


import torch
import pandas as pd
import joblib
from torch_models import MLPClassifier
from dataloader import preprocess_sample

# Config
MODEL_PATH = "./reports/model_best.pth"
FEATURES_FILE = "./reports/feature_importance.csv"
TOP_K = 8 
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Carica le top-8 feature usate in training
features = pd.read_csv(FEATURES_FILE).head(TOP_K)["feature"].tolist()

# Inizializza modello con input_dim = 8
input_dim = len(features)
model = MLPClassifier(input_dim=input_dim)
model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
model.to(DEVICE)
model.eval()

print(f"[INFO] Modello caricato con {input_dim} input features.")

def predict(sample: dict):
    """
    Prevede se un campione appartiene a traffico 'normal' o 'attack'.

    sample: dizionario con tutte le 41 feature originali del dataset NSL-KDD,
    da cui verranno selezionate solo le 8 usate in training.
    """
    # Preprocessing (encoder + scaler salvati, riduzione alle top-8 features)
    X = preprocess_sample(sample, features=features)
    X_tensor = torch.tensor(X, dtype=torch.float32).to(DEVICE)

    with torch.no_grad():
        outputs = model(X_tensor)
        _, predicted = torch.max(outputs, 1)

    label = int(predicted.item())
    return "normal" if label == 0 else "attack"


if __name__ == "__main__":
    # esempio con valori casuali ma plausibili
    sample_example = {
        "duration": 0,
        "protocol_type": "tcp",
        "service": "http",
        "flag": "SF",
        "src_bytes": 181,
        "dst_bytes": 5450,
        "count": 9,"src_bytes": 181,
        "dst_bytes": 5450,
        "same_srv_rate": 1.0,
        "dst_host_srv_count": 9,
        "dst_host_same_srv_rate": 1.0,
        "flag": "SF",
        "logged_in": 1,
        "diff_srv_rate": 0.0
        # top 8 features
    }

    print("Predizione esempio sul sample:", predict(sample_example))

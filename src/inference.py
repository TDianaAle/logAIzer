import argparse
import joblib
import pandas as pd
import json
from pathlib import Path


def preprocess_sample(sample,
    features_file="reports/feature_importance.csv",
    top_k=20,
    encoder_path="reports/encoders.joblib",
    scaler_path="reports/scaler.joblib"):

    """
    Preprocessa un singolo sample nello stesso modo dei dati di training.
    Tiene conto delle feature selezionate.
    """
    
    encoders = joblib.load(encoder_path)
    scaler = joblib.load(scaler_path)

    df = pd.DataFrame([sample])

    # Encoding categoriche
    for col in ["protocol_type", "service", "flag"]:
        if col in df.columns and col in encoders:
            df[col] = encoders[col].transform(df[col])

    # Carica feature selezionate
    feat_df = pd.read_csv(features_file)
    selected_features = feat_df.head(top_k)["feature"].tolist()

    # Seleziona solo le feature usate in training
    df = df[selected_features]

    # Scaling
    X = scaler.transform(df)
    return X


def main(sample_file):
    model_path = Path("reports/random_forest_model.joblib")
    if not model_path.exists():
        raise FileNotFoundError(f" Modello non trovato: {model_path}. Esegui prima train.py")

    # Carica modello
    model = joblib.load(model_path)

    # Carica sample da file JSON
    with open(sample_file, "r") as f:
        sample = json.load(f)

    # Preprocess sample
    X = preprocess_sample(sample)

    # Predizione
    prediction = model.predict(X)[0]
    label = "Normal" if prediction == 0 else "Attack"

    print(f"Predizione per {sample_file}: {label}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--sample", type=str, required=True,
                        help="Percorso al file JSON contenente le feature del sample")
    args = parser.parse_args()

    main(args.sample)

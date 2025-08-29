import json
import joblib
import argparse
import jsonschema
import seaborn as sns
import matplotlib.pyplot as plt

from pathlib import Path
from models import get_models
from dataloader import load_data
from sklearn.metrics import classification_report, confusion_matrix

def save_report(report, model_name, reports_dir):
    """Salva classification report in JSON"""
    report_path = Path(reports_dir) / f"{model_name}_report.json"
    with open(report_path, "w") as f:
        json.dump(report, f, indent=4)
    print(f"Report salvato in {report_path}")

def save_confusion_matrix(y_true, y_pred, model_name, reports_dir):
    """Salva confusion matrix come immagine PNG"""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
        xticklabels=["Normal","Attack"],
        yticklabels=["Normal","Attack"])
    plt.title(f"Confusion Matrix - {model_name}")
    plt.ylabel("True label")
    plt.xlabel("Predicted label")

    cm_path = Path(reports_dir) / f"{model_name}_cm.png"
    plt.savefig(cm_path)
    plt.close()
    print(f"Confusion matrix salvata in {cm_path}")

def main(config_path, schema_path):
    # Carica configurazione e schema
    with open(config_path, "r") as f:
        config = json.load(f)
    with open(schema_path, "r") as f:
        schema = json.load(f)
    jsonschema.validate(instance=config, schema=schema)

    data_cfg = config["data"]
    output_cfg = config["output"]

    Path(output_cfg["reports_dir"]).mkdir(parents=True, exist_ok=True)

    # Carica dati
    X_train, y_train, X_test, y_test = load_data(
        data_cfg["train_path"],
        data_cfg["test_path"],
        binary=data_cfg.get("binary", True),
        features_file=data_cfg.get("features_file", None),
        top_k=data_cfg.get("top_k", None)
    )

    # Ottiene modelli (passa X_train, y_train per RF ottimizzata)
    models = get_models(X_train, y_train)

    for name, model in models.items():
        print(f"\n Addestramento modello: {name}")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)

        # Report di classificazione
        report = classification_report(y_test, y_pred, output_dict=True)
        save_report(report, name, output_cfg["reports_dir"])

        # Confusion matrix
        save_confusion_matrix(y_test, y_pred, name, output_cfg["reports_dir"])

        # Salvataggio modello
        model_path = Path(output_cfg["reports_dir"]) / f"{name}_model.joblib"
        joblib.dump(model, model_path)
        print(f"Modello salvato in {model_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, required=True, help="Percorso file config.json")
    parser.add_argument("--schema", type=str, required=True, help="Percorso file config_schema.json")
    args = parser.parse_args()

    main(args.config, args.schema)

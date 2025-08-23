# src/evaluate.py

import json
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import classification_report, confusion_matrix


def generate_classification_report(y_true, y_pred, output_path=None):
    """
    Genera un classification report (precision, recall, f1, support).
    Se output_path è fornito, salva il report in formato JSON.
    """
    report = classification_report(y_true, y_pred, digits=4, output_dict=True)
    
    if output_path:
        with open(output_path, "w") as f:
            json.dump(report, f, indent=4)
        print(f"[INFO] Report salvato in {output_path}")
    
    return report


def plot_confusion_matrix(y_true, y_pred, model_name="Model", output_path=None):
    """
    Genera e mostra la confusion matrix.
    Se output_path è fornito, salva l’immagine su file.
    """
    cm = confusion_matrix(y_true, y_pred)
    
    plt.figure(figsize=(6,5))
    sns.heatmap(cm, annot=True, fmt="d", cmap="Blues", cbar=False)
    plt.title(f"Confusion Matrix - {model_name}")
    plt.xlabel("Predicted")
    plt.ylabel("True")
    
    if output_path:
        plt.savefig(output_path)
        print(f"[INFO] Confusion matrix salvata in {output_path}")
    else:
        plt.show()

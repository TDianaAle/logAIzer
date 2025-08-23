# src/train.py

import os
import json
import argparse
import jsonschema

from dataloader import DataLoader
from models import get_logistic_regression, get_random_forest
from evaluate import generate_classification_report, plot_confusion_matrix


def load_config(config_path="config.json", schema_path="config_schema.json"):
    """Carica e valida la configurazione"""
    with open(config_path) as f:
        config = json.load(f)
    with open(schema_path) as f:
        schema = json.load(f)
    jsonschema.validate(instance=config, schema=schema)
    return config


def run_training(config):
    """Esegue il training e la valutazione dei modelli definiti in config.json"""
    # Dataset
    dl = DataLoader(config["data"]["train_path"], config["data"]["test_path"])
    train, test = dl.load_data()
    X_train, y_train = dl.preprocess(train, binary=config["data"]["binary"])
    X_test, y_test = dl.preprocess(test, binary=config["data"]["binary"])

    # Output directory
    reports_dir = config["output"]["reports_dir"]
    os.makedirs(reports_dir, exist_ok=True)

    # Logistic Regression
    if config["models"]["logistic_regression"]["enabled"]:
        params = {k: v for k, v in config["models"]["logistic_regression"].items() if k != "enabled"}
        model = get_logistic_regression(params)
        print("\n=== Training Logistic Regression ===")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        generate_classification_report(y_test, y_pred, os.path.join(reports_dir, "lr_report.json"))
        plot_confusion_matrix(y_test, y_pred, "Logistic Regression", os.path.join(reports_dir, "lr_cm.png"))

    # Random Forest
    if config["models"]["random_forest"]["enabled"]:
        params = {k: v for k, v in config["models"]["random_forest"].items() if k != "enabled"}
        model = get_random_forest(params)
        print("\n=== Training Random Forest ===")
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        generate_classification_report(y_test, y_pred, os.path.join(reports_dir, "rf_report.json"))
        plot_confusion_matrix(y_test, y_pred, "Random Forest", os.path.join(reports_dir, "rf_cm.png"))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", type=str, default="config.json", help="Path al file di configurazione")
    parser.add_argument("--schema", type=str, default="config_schema.json", help="Path al file di schema JSON")
    args = parser.parse_args()

    config = load_config(args.config, args.schema)
    run_training(config)

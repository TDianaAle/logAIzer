# src/models.py

from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier

def get_logistic_regression(params=None):
    """
    Restituisce un modello di Logistic Regression.
    Se params è fornito, aggiorna i parametri di default.
    """
    default_params = {
        "max_iter": 1000,
        "class_weight": "balanced",
        "solver": "lbfgs"
    }
    if params:
        default_params.update(params)
    return LogisticRegression(**default_params)

def get_random_forest(params=None):
    """
    Restituisce un modello di Random Forest.
    Se params è fornito, aggiorna i parametri di default.
    """
    default_params = {
        "n_estimators": 100,
        "class_weight": "balanced",
        "random_state": 42
    }
    if params:
        default_params.update(params)
    return RandomForestClassifier(**default_params)

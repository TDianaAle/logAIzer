# src/models.py

from sklearn.linear_model import SGDClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import GridSearchCV

# Logistic Regression con early stopping tramite SGDClassifier anziche LogisticRegression di Scikit
def logistic_regression_model():
    model = SGDClassifier(
        loss="log_loss",     
        max_iter=1000,
        tol=1e-3,
        early_stopping=True,
        n_iter_no_change=5,
        validation_fraction=0.1,
        class_weight="balanced",
        random_state=42
    )
    return model


# Random Forest con GridSearchCV
def random_forest_model(X_train, y_train):
    param_grid = {
        "n_estimators": [100, 200],
        "max_depth": [None, 10, 20],
        "min_samples_split": [2, 5],
        "min_samples_leaf": [1, 2],
        "max_features": ["sqrt", "log2"]
    }

    rf = RandomForestClassifier(class_weight="balanced", random_state=42, n_jobs=-1)

    grid_search = GridSearchCV(
        estimator=rf,
        param_grid=param_grid,
        cv=3,
        scoring="f1",
        n_jobs=-1,
        verbose=2
    )

    grid_search.fit(X_train, y_train)

    print(" Migliori parametri Random Forest:", grid_search.best_params_)
    best_model = grid_search.best_estimator_
    return best_model


# Funzione che ritorna i modelli
def get_models(X_train=None, y_train=None):
    models = {}
    models["logistic_regression"] = logistic_regression_model()

    if X_train is not None and y_train is not None:
        models["random_forest"] = random_forest_model(X_train, y_train)

    return models

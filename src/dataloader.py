# src/dataloader.py
import pandas as pd
import joblib
import os
from sklearn.preprocessing import LabelEncoder, StandardScaler

def load_data(train_path, test_path, binary=True, features_file=None, top_k=None):
    """
    Carica e preprocessa il dataset NSL-KDD.
    """
    # Nomi delle colonne NSL-KDD
    columns = [
        "duration","protocol_type","service","flag","src_bytes","dst_bytes","land",
        "wrong_fragment","urgent","hot","num_failed_logins","logged_in","num_compromised",
        "root_shell","su_attempted","num_root","num_file_creations","num_shells","num_access_files",
        "num_outbound_cmds","is_host_login","is_guest_login","count","srv_count","serror_rate",
        "srv_serror_rate","rerror_rate","srv_rerror_rate","same_srv_rate","diff_srv_rate",
        "srv_diff_host_rate","dst_host_count","dst_host_srv_count","dst_host_same_srv_rate",
        "dst_host_diff_srv_rate","dst_host_same_src_port_rate","dst_host_srv_diff_host_rate",
        "dst_host_serror_rate","dst_host_srv_serror_rate","dst_host_rerror_rate",
        "dst_host_srv_rerror_rate","label","difficulty"
    ]

    # Caricamento dataset
    train = pd.read_csv(train_path, names=columns)
    test = pd.read_csv(test_path, names=columns)

    # Etichetta binaria anziché multiclass
    if binary:
        train["binary_label"] = train["label"].apply(lambda x: 0 if x == "normal" else 1)
        test["binary_label"] = test["label"].apply(lambda x: 0 if x == "normal" else 1)
        target = "binary_label"
    else:
        target = "label"

    # Encoding categoriche
    encoders = {}
    for col in ["protocol_type", "service", "flag"]:
        le = LabelEncoder()
        train[col] = le.fit_transform(train[col])
        test[col] = le.transform(test[col])
        encoders[col] = le

    # Selezione feature più importanti
    selected_features = None
    if features_file is not None:
        feat_df = pd.read_csv(features_file)
        if top_k is not None:
            selected_features = feat_df.head(top_k)["feature"].tolist()
        else:
            selected_features = feat_df["feature"].tolist()

    drop_cols = ["label", "difficulty", target]
    X_train = train.drop(columns=drop_cols)
    X_test = test.drop(columns=drop_cols)

    if selected_features:
        X_train = X_train[selected_features]
        X_test = X_test[selected_features]

    y_train = train[target]
    y_test = test[target]

    # Scaling
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)

    # === Salvataggio encoder e scaler per l'inference ===
    REPORTS_DIR = "../reports"
    os.makedirs(REPORTS_DIR, exist_ok=True)

    joblib.dump(encoders, os.path.join(REPORTS_DIR, "encoders.joblib"))
    joblib.dump(scaler, os.path.join(REPORTS_DIR, "scaler.joblib"))

    return X_train, y_train, X_test, y_test


def preprocess_sample(
    sample,
    encoder_path="../reports/encoders.joblib",
    scaler_path="../reports/scaler.joblib",
    features=None
):
    """
    Preprocessa un singolo campione (dict) per l'inference.
    """
    # Carica encoder e scaler
    encoders = joblib.load(encoder_path)
    scaler = joblib.load(scaler_path)

    df = pd.DataFrame([sample])

    # Encoding delle categoriche
    for col in ["protocol_type", "service", "flag"]:
        if col in df.columns and col in encoders:
            df[col] = encoders[col].transform(df[col])

    if features is not None:
        df = df[features]

    X = scaler.transform(df)
    return X

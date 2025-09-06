# src/dataloader.py
import os
import joblib
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.preprocessing import LabelEncoder, StandardScaler

def load_data(train_path, test_path, binary=True, features_file="../reports/feature_importance.csv", top_k=8):
    """
    Carica e preprocessa il dataset NSL-KDD, selezionando solo le top-k feature (default: 8).
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

    # Carica top-k feature dall’EDA
    feat_df = pd.read_csv(features_file)
    selected_features = feat_df.head(top_k)["feature"].tolist()

    # Seleziona solo le top-k feature
    X_train = train[selected_features]
    X_test = test[selected_features]
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


if __name__ == "__main__":
    TRAIN_PATH = "./data/nsl-kdd/KDDTrain+.txt"
    TEST_PATH = "./data/nsl-kdd/KDDTest+.txt"
    FEATURES_FILE = "./reports/feature_importance.csv"
    TOP_K = 8  #sempre le top 8

    print("[INFO] Loading dataset...")
    X_train, y_train, X_test, y_test = load_data(
        train_path=TRAIN_PATH,
        test_path=TEST_PATH,
        binary=True,
        features_file=FEATURES_FILE,
        top_k=TOP_K
    )

    print("[INFO] Dataset loaded successfully!")
    print(f" - Training set shape: {X_train.shape}, Labels: {y_train.shape}")
    print(f" - Test set shape:     {X_test.shape}, Labels: {y_test.shape}")
    print(f" - Example labels distribution (train):\n{y_train.value_counts().head()}")

    # Grafico distribuzione classi
    plt.figure(figsize=(5,4))
    y_train.value_counts().plot(kind="bar")
    plt.title("Distribuzione classi nel training set")
    plt.xlabel("Classe (0=normal, 1=attack)")
    plt.ylabel("Numero campioni")
    plt.show()

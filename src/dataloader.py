import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

def load_and_preprocess(train_path, test_path, features_to_keep=None):
    # Colonne ufficiali
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

    # Caricamento dati
    train = pd.read_csv(train_path, names=columns)
    test = pd.read_csv(test_path, names=columns)

    # Target binario
    for df in (train, test):
        df["binary_label"] = df["label"].apply(lambda x: 0 if x == "normal" else 1)

    # Encoding categoriche
    encoder = LabelEncoder()
    for col in ["protocol_type", "service", "flag"]:
        train[col] = encoder.fit_transform(train[col])
        test[col] = encoder.transform(test[col])

    # X, y
    X_train = train.drop(columns=["label", "difficulty", "binary_label"])
    y_train = train["binary_label"]
    X_test = test.drop(columns=["label", "difficulty", "binary_label"])
    y_test = test["binary_label"]

    # Selezione feature più importanti
    if features_to_keep is not None:
        X_train = X_train[features_to_keep]
        X_test = X_test[features_to_keep]

    # Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    return X_train_scaled, X_test_scaled, y_train, y_test

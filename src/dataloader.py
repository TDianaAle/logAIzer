# src/dataloader.py

import pandas as pd
from sklearn.preprocessing import LabelEncoder, StandardScaler

# Definizione delle colonne del dataset NSL-KDD
COLUMNS = [
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

class DataLoader:
    def __init__(self, train_path, test_path):
        self.train_path = train_path
        self.test_path = test_path
        self.encoder = LabelEncoder()
        self.scaler = StandardScaler()

    def load_data(self):
        """Carica dataset train e test"""
        train = pd.read_csv(self.train_path, names=COLUMNS)
        test = pd.read_csv(self.test_path, names=COLUMNS)
        return train, test

    def preprocess(self, df, binary=True):
        """Preprocessamento: encoding e scaling"""
        # Encoding variabili categoriche
        for col in ["protocol_type", "service", "flag"]:
            df[col] = self.encoder.fit_transform(df[col])

        # Target binario o multiclass
        if binary:
            df["target"] = df["label"].apply(lambda x: 0 if x == "normal" else 1)
        else:
            df["target"] = df["label"]

        # Drop colonne non utili
        X = df.drop(columns=["label", "difficulty", "target"])
        y = df["target"]

        # Scaling
        X_scaled = self.scaler.fit_transform(X)
        return X_scaled, y

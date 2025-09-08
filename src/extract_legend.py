import pandas as pd
from dataloader import load_data

# Config
TRAIN_PATH = "./data/nsl-kdd/KDDTrain+.txt"
TEST_PATH = "./data/nsl-kdd/KDDTest+.txt"
FEATURES_FILE = "./reports/feature_importance.csv"
TOP_K = 8

# Carica dataset completo
X_train, y_train, X_test, y_test, encoders, scaler = load_data(
    train_path=TRAIN_PATH,
    test_path=TEST_PATH,
    binary=False,                 
    features_file=FEATURES_FILE,
    top_k=TOP_K
)


df_train = pd.read_csv(TRAIN_PATH, header=None)
df_test = pd.read_csv(TEST_PATH, header=None)
df_full = pd.concat([df_train, df_test], ignore_index=True)

# Colonne NSL-KDD
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
df_full.columns = columns

# Carica top-K features scelte
feat_df = pd.read_csv(FEATURES_FILE)
selected_features = feat_df.head(TOP_K)["feature"].tolist()

# Classi di interesse
cases = {
    "Normale": "normal",
    "TCP Flood (DoS)": "neptune",
    "Brute Force": "guess_passwd",
    "Probe": "ipsweep"
}

legend_rows = []

for case, label in cases.items():
    subset = df_full[df_full["label"] == label]

    if subset.empty:
        print(f"[WARN] Nessun esempio per {label}")
        continue

    row = {"Caso": case}

    for feat in selected_features:
        if subset[feat].dtype == "object":
            row[feat] = subset[feat].mode().iloc[0]  # moda per categoriche
        else:
            row[feat] = int(subset[feat].median())   # mediana per numeriche

    row["Risultato previsto"] = "normal" if label == "normal" else "attack"
    legend_rows.append(row)

legend_df = pd.DataFrame(legend_rows)

print("\n=== LEGENDA CALCOLATA SULLE 8 FEATURE TOP-K ===\n")
print(legend_df.to_markdown(index=False))

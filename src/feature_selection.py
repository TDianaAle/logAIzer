import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier

# ===  Caricamento dataset ===
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

train = pd.read_csv("data/nsl-kdd/KDDTrain+.TXT", names=columns)

# ===  Preprocessing ===
train["binary_label"] = train["label"].apply(lambda x: 0 if x == "normal" else 1)

encoder = LabelEncoder()
for col in ["protocol_type", "service", "flag"]:
    train[col] = encoder.fit_transform(train[col])

X = train.drop(columns=["label", "difficulty", "binary_label"])
y = train["binary_label"]

scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# === Training Random Forest ===
rf = RandomForestClassifier(n_estimators=100, random_state=42, class_weight="balanced")
rf.fit(X_scaled, y)

importances = rf.feature_importances_
feature_names = X.columns

feature_importance = pd.DataFrame({
    "feature": feature_names,
    "importance": importances
}).sort_values(by="importance", ascending=False)

# === Salvataggio risultati ===
feature_importance.to_csv("reports/feature_importance.csv", index=False)

plt.figure(figsize=(12,8))
sns.barplot(data=feature_importance.head(20), x="importance", y="feature", palette="viridis")
plt.title("Top 20 Feature per importanza (Random Forest)", fontsize=14)
plt.xlabel("Importanza")
plt.ylabel("Feature")
plt.tight_layout()
plt.savefig("reports/feature_importance.png")
plt.close()

print(" Feature importance salvata in reports/feature_importance.csv e reports/feature_importance.png")

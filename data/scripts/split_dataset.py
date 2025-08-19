import pandas as pd
from sklearn.model_selection import train_test_split
import os

# Percorsi
PROCESSED_DIR = "data/processed"
DATASET_FILE = os.path.join(PROCESSED_DIR, "unsw_gt_normalized.csv")
OUTPUT_DIR = os.path.join(PROCESSED_DIR, "splits")

# Crea la cartella splits se non esiste
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Carica il dataset pulito
df = pd.read_csv(DATASET_FILE)

# Dividi train (80%) e test (20%)
train_df, test_df = train_test_split(df, test_size=0.2, random_state=42, stratify=df["Attack category"])

# Salva i file
train_df.to_csv(os.path.join(OUTPUT_DIR, "train.csv"), index=False)
test_df.to_csv(os.path.join(OUTPUT_DIR, "test.csv"), index=False)

print(f"✅ Dataset diviso in:")
print(f"- Train set: {train_df.shape[0]} righe salvato in {OUTPUT_DIR}/train.csv")
print(f"- Test set: {test_df.shape[0]} righe salvato in {OUTPUT_DIR}/test.csv")

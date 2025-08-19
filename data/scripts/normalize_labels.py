#all'avvio dello script eda_gt.py sono comparsi dei conflitti tra label, con questo script si risolvono

# data/scripts/normalize_labels.py
import pandas as pd
from pathlib import Path

# Path
input_path = Path("data/reduced/UNSW-NB15_GT.csv")   # file originale
output_path = Path("data/processed/unsw_gt_normalized.csv")  # file pulito
output_path.parent.mkdir(parents=True, exist_ok=True)

# Caricamento dataset
print(f"Caricamento {input_path}...")
df = pd.read_csv(input_path)

# Normalizzazione delle etichette
df["Attack category"] = df["Attack category"].str.lower().str.strip()

# Mappatura per unificare le etichette incoerenti
mapping = {
    "backdoors": "backdoor",
    "fuzzers": "fuzzer",
    "generic ": "generic",  # rimuove eventuali spazi extra
    "shellcode": "shellcode",  # lasciamo invariato
    "analysis ": "analysis"
}

df["Attack category"] = df["Attack category"].replace(mapping)

# Salvataggio
df.to_csv(output_path, index=False)
print(f"✅ File normalizzato salvato in {output_path}")

# Controllo categorie finali
print("\nCategorie finali:")
print(df["Attack category"].value_counts())

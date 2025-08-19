import os
import pandas as pd

# cartelle input/output
RAW_DIR = "data/CICIDS2017"
OUT_DIR = "data/reduced"
os.makedirs(OUT_DIR, exist_ok=True)

# dimensione massima consentita (in byte → 50MB)
MAX_SIZE = 50 * 1024 * 1024

# ciclo su tutti i csv nella cartella raw
for file in os.listdir(RAW_DIR):
    if file.endswith(".csv"):
        input_path = os.path.join(RAW_DIR, file)
        output_path = os.path.join(OUT_DIR, file)

        print(f"\nProcessing {file} ...")

        # leggo solo la dimensione attuale
        file_size = os.path.getsize(input_path)
        print(f" - Original size: {file_size/1024/1024:.2f} MB")

        # carico dataset
        df = pd.read_csv(input_path)

        # calcolo frazione necessaria
        frac = min(1.0, MAX_SIZE / file_size)
        print(f" - Sampling fraction: {frac:.3f}")

        if frac < 1.0:
            df_sample = df.sample(frac=frac, random_state=42)
        else:
            df_sample = df

        # salvo ridotto
        df_sample.to_csv(output_path, index=False)

        new_size = os.path.getsize(output_path)
        print(f" - Reduced size: {new_size/1024/1024:.2f} MB")

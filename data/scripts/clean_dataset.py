import pandas as pd

# Carica il dataset GT
df_gt = pd.read_csv("data/reduced/UNSW-NB15_GT.csv")

# Controlla le prime righe
print(df_gt.head())

# Controlla valori mancanti
print(df_gt.isna().sum())

# Converte colonne temporali in datetime
df_gt['Start time'] = pd.to_datetime(df_gt['Start time'], unit='s')
df_gt['Last time'] = pd.to_datetime(df_gt['Last time'], unit='s')

# Converte porte in interi
df_gt['Source Port'] = pd.to_numeric(df_gt['Source Port'], errors='coerce').fillna(0).astype(int)
df_gt['Destination Port'] = pd.to_numeric(df_gt['Destination Port'], errors='coerce').fillna(0).astype(int)

# Eventuale rimozione colonne inutili (ad esempio '.')
if '.' in df_gt.columns:
    df_gt = df_gt.drop(columns=['.'])

# Controlla tipo colonne
print(df_gt.dtypes)
df_gt.to_csv("data/processed/unsw_gt_cleaned.csv", index=False)
import pandas as pd
from sklearn.preprocessing import OneHotEncoder, StandardScaler
import os

# Percorsi dei file ridotti
unsw_files = [
    'data/reduced/UNSW-NB15_1.csv',
    'data/reduced/UNSW-NB15_2.csv',
    'data/reduced/UNSW-NB15_3.csv',
    'data/reduced/UNSW-NB15_4.csv'
]
gt_file = 'data/reduced/UNSW-NB15_GT.csv'  # ground truth

# Unire i dataset UNSW-NB15
dfs = [pd.read_csv(f) for f in unsw_files]
df_unsw = pd.concat(dfs, ignore_index=True)

# Caricare ground truth
df_gt = pd.read_csv(gt_file)

# Unire df_unsw con df_gt usando la colonna comune (ad esempio 'id' o 'Flow ID')
# Sostituire 'id' con la colonna corretta che identifica univocamente i flussi
df = df_unsw.merge(df_gt, on='id', how='left')  # left join mantiene tutti i dati UNSW

# Pulizia dati mancanti
df = df.dropna()

# Separare features e target
target_col = 'Attack category'  # o 'Label' se gt ha una colonna Label
X = df.drop(columns=[target_col])
y = df[target_col]

# Identificare colonne categoriche
categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
numeric_cols = X.select_dtypes(include=['int64', 'float64']).columns.tolist()

# One-hot encoding delle colonne categoriche
if categorical_cols:
    encoder = OneHotEncoder(sparse=False, handle_unknown='ignore')
    X_cat = pd.DataFrame(encoder.fit_transform(X[categorical_cols]))
    X_cat.index = X.index
    X = X.drop(columns=categorical_cols)
    X = pd.concat([X, X_cat], axis=1)

# Standardizzazione dei valori numerici
if numeric_cols:
    scaler = StandardScaler()
    X[numeric_cols] = scaler.fit_transform(X[numeric_cols])

# Ricreare il dataframe completo con target
df_processed = pd.concat([X, y], axis=1)

# Creare cartella processed se non esiste
os.makedirs('data/processed', exist_ok=True)

# Salvare il dataset preprocessato
df_processed.to_csv('data/processed/unsw_nb15_with_gt_processed.csv', index=False)

print("Dataset UNSW-NB15 + GT preprocessato e salvato in 'data/processed/unsw_nb15_with_gt_processed.csv'")

import pandas as pd
import matplotlib.pyplot as plt

# Carica il dataset GT pulito
file_path = "data/processed/unsw_gt_cleaned.csv"
df = pd.read_csv(file_path)

# Info di base
print("🔹 Dimensioni dataset:", df.shape)
print("\n🔹 Prime righe:")
print(df.head())

print("\n🔹 Tipi di dati:")
print(df.dtypes)

print("\n🔹 Valori nulli per colonna:")
print(df.isnull().sum())

# Distribuzione delle categorie di attacco
print("\n🔹 Distribuzione delle categorie di attacco:")
print(df["Attack category"].value_counts())

# Grafico distribuzione attacchi
plt.figure(figsize=(10,6))
df["Attack category"].value_counts().plot(kind="bar")
plt.title("Distribuzione degli attacchi (GT)")
plt.xlabel("Categoria attacco")
plt.ylabel("Numero campioni")
plt.tight_layout()
plt.show()

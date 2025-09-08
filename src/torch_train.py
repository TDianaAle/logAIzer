# src/torch_train.py
import torch
import joblib
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader
from torch.utils.tensorboard import SummaryWriter

import numpy as np
import os

from .dataloader import load_data
from .torch_models import MLPClassifier

# === CONFIGURAZIONE ===
TRAIN_PATH = "./data/nsl-kdd/KDDTrain+.txt"
TEST_PATH = "./data/nsl-kdd/KDDTest+.txt"
FEATURES_FILE = "./reports/feature_importance.csv"
TOP_K = 8   # selezionate solo le 8 feature piu rilevanti

BATCH_SIZE = 64
EPOCHS = 50
LEARNING_RATE = 1e-3
PATIENCE = 5  # early stopping

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# === CARICAMENTO DATI ===
print("[INFO] Caricamento dataset...")
X_train, y_train, X_test, y_test, encoders, scaler = load_data(
    train_path=TRAIN_PATH,
    test_path=TEST_PATH,
    binary=True,
    features_file=FEATURES_FILE,
    top_k=TOP_K
)
REPORTS_DIR = "./reports"
os.makedirs(REPORTS_DIR, exist_ok=True)
joblib.dump(encoders, os.path.join(REPORTS_DIR, "encoders.joblib"))
joblib.dump(scaler, os.path.join(REPORTS_DIR, "scaler.joblib"))

input_dim = X_train.shape[1]
print(f"[INFO] Numero di feature usate per il training: {input_dim}")

# Conversione in tensori
X_train_tensor = torch.tensor(X_train, dtype=torch.float32)
y_train_tensor = torch.tensor(y_train.values, dtype=torch.long)
X_test_tensor = torch.tensor(X_test, dtype=torch.float32)
y_test_tensor = torch.tensor(y_test.values, dtype=torch.long)

# Creazione DataLoader
train_dataset = TensorDataset(X_train_tensor, y_train_tensor)
test_dataset = TensorDataset(X_test_tensor, y_test_tensor)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
val_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

# === MODELLO, LOSS E OPTIMIZER ===
model = MLPClassifier(input_dim=input_dim).to(DEVICE)
criterion = nn.CrossEntropyLoss()
optimizer = optim.Adam(model.parameters(), lr=LEARNING_RATE)

# TensorBoard
writer = SummaryWriter(log_dir="./runs/ids_experiment")

print("[INFO] Inizio training MLPClassifier...")
print(model)

# === TRAINING LOOP ===
best_val_loss = float("inf")
patience_counter = 0

for epoch in range(EPOCHS):
    model.train()
    train_losses = []

    for X_batch, y_batch in train_loader:
        X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)

        optimizer.zero_grad()
        outputs = model(X_batch)
        loss = criterion(outputs, y_batch)
        loss.backward()
        optimizer.step()

        train_losses.append(loss.item())

    avg_train_loss = np.mean(train_losses)

    # === VALIDAZIONE ===
    model.eval()
    val_losses = []
    correct, total = 0, 0

    with torch.no_grad():
        for X_batch, y_batch in val_loader:
            X_batch, y_batch = X_batch.to(DEVICE), y_batch.to(DEVICE)
            outputs = model(X_batch)
            loss = criterion(outputs, y_batch)
            val_losses.append(loss.item())

            _, predicted = torch.max(outputs, 1)
            total += y_batch.size(0)
            correct += (predicted == y_batch).sum().item()

    avg_val_loss = np.mean(val_losses)
    val_accuracy = correct / total

    print(f"[EPOCH {epoch+1}/{EPOCHS}] "
            f"Train Loss: {avg_train_loss:.4f} | "
            f"Val Loss: {avg_val_loss:.4f} | "
            f"Val Acc: {val_accuracy:.4f}")

    # TensorBoard logging
    writer.add_scalar("Loss/train", avg_train_loss, epoch)
    writer.add_scalar("Loss/val", avg_val_loss, epoch)
    writer.add_scalar("Accuracy/val", val_accuracy, epoch)

    # === SALVATAGGIO MODELLO ===
    torch.save(model.state_dict(), "./reports/model_last.pth")

    if avg_val_loss < best_val_loss:
        best_val_loss = avg_val_loss
        torch.save(model.state_dict(), "./reports/model_best.pth")
        print("[INFO] → Miglior modello salvato.")
        patience_counter = 0
    else:
        patience_counter += 1

    # Early stopping
    if patience_counter >= PATIENCE:
        print("[INFO] Early stopping attivato.")
        break

writer.close()
print("[INFO] Training completato.")

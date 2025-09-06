# src/torch_models.py
import torch
import torch.nn as nn
import torch.nn.functional as F

class MLPClassifier(nn.Module):
    """
    Multilayer Perceptron (MLP) per classificazione binaria del traffico di rete.
    Architettura:
    - Input layer con dimensione pari al numero di feature selezionate (es. 8).
    - Due hidden layer fully-connected con ReLU + Dropout.
    - Output layer con 2 neuroni (classi: normal, attack).
    """

    def __init__(self, input_dim, hidden_dim=64, output_dim=2, dropout=0.3):
        super(MLPClassifier, self).__init__()

        self.network = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Dropout(dropout),
            
            nn.Linear(hidden_dim, output_dim)
        )

    def forward(self, x):
        return self.network(x)


if __name__ == "__main__":
    # Simulazione test modello
    INPUT_DIM = 8  # numero di feature selezionate
    dummy_input = torch.randn(4, INPUT_DIM)  # batch fittizio con 4 campioni

    model = MLPClassifier(input_dim=INPUT_DIM)

    print("\n[INFO] MLPClassifier inizializzato con successo")
    print(model)

    outputs = model(dummy_input)
    print(f"\n[INFO] Input shape: {dummy_input.shape}")
    print(f"[INFO] Output shape: {outputs.shape}")

    # Probabilità e predizioni simulate
    probs = F.softmax(outputs, dim=1)
    preds = torch.argmax(probs, dim=1)

    print("\n[INFO] Esempio prediction su dummy input:")
    for i, (p, pr) in enumerate(zip(probs, preds)):
        print(f" - Sample {i+1}: probs={p.detach().numpy()}, predicted_class={pr.item()}")

    print("\n[INFO] Test eseguito correttamente: il modello è pronto per l'addestramento.\n")

ECHO attivo.
# LogAIzer Project

Documentazione Tecnica – Progetto LogAIzer

1. Dataset di partenza

 Scelto il dataset UNSW-NB15 Ground Truth (GT).
Questo dataset contiene etichette di traffico di rete con categorie di attacchi informatici (es. DoS, Exploits, Backdoor, Analysis, Fuzzers, Generic, Reconnaissance, Shellcode, Worms, Normal).
Le colonne principali includono:

Start time, Last time → timestamp di inizio/fine sessione

Protocol, Source IP, Source Port, Destination IP, Destination Port → informazioni di rete

Attack category, Attack subcategory → etichette per la classificazione

2. Gestione dei dati raw

I dataset originali erano troppo grandi (>50 MB ciascuno) e non caricabili su GitHub.

Ho scritto uno script (new_size_script.py) per ridurli, mantenendo subset <50MB.

I file ridotti sono stati salvati in data/reduced/.

per più informazioni riguardo al dataset utilizzato consultare la seguente pagina web:
https://research.unsw.edu.au/projects/unsw-nb15-dataset

4. Normalizzazione e pulizia

Creato uno script (normalize_gt.py) che:

Carica il dataset GT.

Uniforma le categorie (es. backdoor e backdoors → Backdoor).

Salva la versione pulita in data/processed/unsw_gt_normalized.csv.

5. Analisi esplorativa iniziale

Contato le classi presenti nella colonna Attack category.

Risultato: dataset sbilanciato, con alcune classi molto più presenti di altre (es. Generic è molto più numerosa di Worms).

Questa informazione sarà importante per il bilanciamento del modello.

6. Suddivisione Train/Test

Creato lo script split_dataset.py, che:

Carica unsw_gt_normalized.csv.

Divide i dati in 80% training set e 20% test set.

Usa train_test_split(..., stratify=y) per mantenere le proporzioni delle classi.

Salva i file in:

data/processed/splits/train.csv

data/processed/splits/test.csv

Output esempio:

✅ Dataset diviso in:

- Train set: XXXXX righe salvato in data/processed/splits/train.csv
- Test set: YYYY righe salvato in data/processed/splits/test.csv


🔜 Prossimi passi

Analisi esplorativa più approfondita (EDA)

Verificare distribuzione delle feature (es. protocolli più usati, porte più comuni, distribuzione temporale degli attacchi).

Visualizzare sbilanciamento delle classi con grafici.

Preprocessing avanzato

One-hot encoding delle feature categoriali (Protocol, Attack category, ecc.).

Normalizzazione/scaling delle feature numeriche.

Addestramento modello ML

Modelli candidati: Random Forest, Gradient Boosting, o una Rete Neurale.

Validazione con cross-validation.

Valutazione

Metriche: Accuracy, Precision, Recall, F1-score, Confusion Matrix.

Attenzione particolare alle classi minoritarie (es. Worms).

Deployment su Cloud

Esporre il modello via API (FastAPI/Flask).

Rendere disponibile il servizio a un’app web esterna che può inviare dati di rete e ricevere la classificazione.

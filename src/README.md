
#  logAIzer – Modulo  Artificial Intelligence & Machine Learning

Il modulo ML di logAIzer implementa una pipeline per l’addestramento e la valutazione di modelli di classificazione sul dataset NSL-KDD, con l’obiettivo di sviluppare un sistema di Intrusion Detection (IDS) basato su tecniche di analisi dati e apprendimento automatico, in grado si analizzare traffico di rete in tempo reale, classificando eventi come normali, o in caso di traffico sospetto, come possbile attacco.

 #  Struttura del progetto
src/
│── dataloader.py # Caricamento, preprocessing e scaling dei dati
│── feature_selection.py # selezione delle feature più rilevanti
│── models.py # Definizione e ottimizzazione dei modelli ML
│── train.py # Pipeline di training, validazione e salvataggio
│── inference.py # Predizioni su nuovi campioni
config.json # File di configurazione
config_schema.json # Schema JSON per validazione
reports/ # Output di metriche, modelli e confusion matrix


## Come avviare l’IDS

Il progetto è strutturato in due fasi principali:

1. **Preparazione e training del modello** (offline, con i file in `src/` e il dataset NSL-KDD).  
2. **Rilevamento in tempo reale** (online, con `IDS/packet_sniffer.py`).  

---

### Prima fase, offline

Questa fase si svolge in due ambienti:

- **`notebook.ipynb`** → contiene tutta la parte di analisi dati (EDA) sul dataset NSL-KDD: caricamento, preprocessing, encoding, scaling, feature selection. Da qui vengono prodotti gli artefatti fondamentali:
  - `encoders.joblib`
  - `scaler.joblib`
  - `reports/feature_importance.csv`

- **`src/`** → contiene gli script modulari per il training del modello:

  - `dataloader.py`  
    Funzioni per caricare il dataset NSL-KDD e restituire `X` (feature) e `y` (etichette).
  
  - `feature_selection.py`  
    Applica la selezione delle feature (basata su Random Forest) e salva il ranking in `reports/feature_importance.csv`.

  - `models.py`  
    Definisce i modelli ML ( Random Forest, Logistic Regression).

  - `train.py`  
    Script principale di training: 
    - Carica i dati dal `dataloader`.  
    - Applica encoding e scaling.  
    - Addestra i modelli definiti in `models.py`.  
    - Salva il modello addestrato in `reports/random_forest_model.joblib`.

  - `inference.py`  
    Permette di testare un modello già addestrato su nuovi dati (es. sul test set NSL-KDD).  

👉 **Ordine di esecuzione tipico (fase offline):**

```bash
# 1. Carica e analizza i dati
jupyter notebook notebook.ipynb

# 2. Esegue la selezione delle feature
python src/feature_selection.py

# 3. Allena il modello e salva i file joblib
python src/train.py

# 4. (Opzionale) Testa il modello addestrato
python src/inference.py

---

Le principali caratteristiche del dataset scelto:

- **41 feature** tra numeriche e categoriche, che descrivono aspetti relativi a connessioni di rete (byte scambiati, protocolli, flag TCP, ecc.).
- **Etichettatura multiclasse** che distingue il traffico in normale e in diverse tipologie di attacco (DoS, Probe, U2R, R2L).
- **Suddivisione in train e test** con differente complessità (indice `difficulty`), pensata per valutare la capacità di generalizzazione dei modelli.

# Preprocessing e riduzione della complessità
Al fine di adattare il dataset all’obiettivo primario di un IDS, ovvero la distinzione tra traffico benigno e malevolo, le etichette multiclasse sono state ridotte ad una classificazione **binaria**:
- `0 = normal`,  
- `1 = attack`.  

Tale scelta risponde alla necessità di semplificare la pipeline di training e garantire risultati chiari nella fase di dimostrazione.

---

## Preprocessing dei dati
### Encoding delle variabili categoriche
Le variabili `protocol_type`, `service` e `flag` sono state trattate con **Label Encoding**, trasformandole da stringhe a rappresentazioni numeriche poiché il Random Forest non richiede feature numeriche scalate su range specifici, ma necessita di un mapping consistente tra training e runtime.  
Per garantire consistenza, gli encoder addestrati sono stati **serializzati in un file unico (`encoders.joblib`)**, in modo da poter essere riutilizzati in fase di sniffing in tempo reale.

### 3.2 Scaling delle feature numeriche
Le variabili numeriche sono state normalizzate tramite **StandardScaler** (media=0, varianza=1). Questa operazione previene distorsioni dovute a grandezze eterogenee (es. `src_bytes` in migliaia di byte contro `diff_srv_rate` in [0,1]).  
Lo scaler è stato anch’esso salvato (`scaler.joblib`) per garantire che i dati runtime vengano trasformati con la stessa distribuzione statistica del training.

### 3.3 Feature Selection
Per ridurre ridondanze e concentrare il modello sulle variabili più informative, è stato applicato un **Random Forest Classifier** addestrato sul dataset preprocessato. L’analisi delle **feature importance** ha evidenziato che ~20 variabili spiegano oltre il 70% della capacità predittiva del modello.  
Tra le più significative: `src_bytes`, `dst_bytes`, `same_srv_rate`, `dst_host_srv_count`, `flag`.  
Le feature a bassa importanza (<0.001) sono state scartate, riducendo rumore e complessità.

---

## Modello di Machine Learning

È stato adottato un **Random Forest Classifier**, per le seguenti ragioni:  
- robustezza a dati rumorosi e outlier,  
- capacità di gestire variabili sia numeriche che categoriche,  
- interpretabilità tramite feature importance,  
- buone prestazioni anche senza tuning estensivo di iperparametri.  

### Parametri
- `n_estimators = 100`  
- `class_weight = "balanced"` (per compensare lo sbilanciamento del dataset)  
- `random_state = 42` (riproducibilità).  

### Metriche ottenute
- **Accuracy complessiva**: >90%.  
- **Recall sugli attacchi**: >85%.  
- **Precision** variabile a seconda della tipologia di attacco, in linea con i limiti intrinseci del dataset.  

Il modello finale è stato salvato in `random_forest_model.joblib`.

---
**PER PROCEDERE CON LA DEMO DEL SOFTWARE, visualizzare il README.md in IDS/.**
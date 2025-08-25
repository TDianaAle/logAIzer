

# 📊 Analisi Dati – NSL-KDD Dataset
 
L’attività di analisi dati condotta sul dataset **NSL-KDD** ha avuto un duplice obiettivo:  
1. fornire una comprensione approfondita della struttura e delle proprietà dei dati;  
2. individuare le criticità e le trasformazioni necessarie affinché il dataset possa essere impiegato in modo efficace in modelli di *Machine Learning* per la realizzazione di un sistema di **Intrusion Detection (IDS)**.

## ℹ️ Documentazione del dataset
Per una descrizione dettagliata della struttura del dataset, delle feature e delle etichette disponibili, 
si rimanda alla pagina [data/nsl-kdd/index.html](data/nsl-kdd/index.html).

---
## Tecnologie utilizzate

# Pandas

Libreria di riferimento in Python per la manipolazione e l’analisi di dataset tabellari,  utilizzata per il caricamento del dataset NSL-KDD, l’assegnazione dei nomi ufficiali delle colonne, l’esplorazione preliminare tramite metodi descrittivi (head(), shape(), describe()),
 l’analisi della distribuzione delle classi (value_counts()).

Grazie alla struttura dei DataFrame, Pandas consente di trattare i dati in modo analogo a una tabella relazionale, rendendo possibili operazioni complesse di filtraggio, raggruppamento e trasformazione con poche righe di codice.
Nel contesto di un IDS, questo strumento ha permesso di passare dal dataset grezzo a una base dati strutturata e coerente, pronta per successive elaborazioni.

# Matplotlib

 Libreria base per la visualizzazione grafica in Python,
 è stata utilizzata in combinazione con Seaborn per la generazione di grafici a barre (countplot), la rappresentazione di boxplot per individuare outlier e la costruzione di heatmap per l’analisi delle correlazioni tra variabili.

# Seaborn

Libreria di data visualization costruita su Matplotlib, con un orientamento specifico verso analisi statistiche, adottata per la necessità di ottenere grafici chiari, leggibili e ottimizzati per l’interpretazione dei dati.

Le funzionalità impiegate includono grafici di distribuzione delle classi (countplot),

boxplot per la rilevazione di valori anomali,

heatmap della matrice di correlazione tra variabili numeriche.

Rispetto a Matplotlib, Seaborn offre un livello di astrazione superiore che consente di focalizzarsi sull’analisi piuttosto che sulla configurazione estetica.
In un IDS, strumenti di questo tipo supportano la comprensione immediata delle caratteristiche distintive tra traffico normale e malevolo.

# Scikit-Learn

Scikit-Learn (sklearn) è la libreria Python più diffusa per l’apprendimento automatico e nella fase di analisi dati è stata impiegata per l’encoding delle variabili categoriche (protocol_type, service, flag) mediante LabelEncoder, la trasformazione dell’etichetta target (normal/attack), e per la standardizzazione delle feature numeriche tramite StandardScaler.

Questi passaggi di preprocessing hanno reso il dataset numericamente consistente e normalizzato, condizione indispensabile per addestrare modelli di Machine Learning.
Senza tali trasformazioni, i modelli sarebbero stati soggetti a bias e instabilità dovute a scale eterogenee o a input non numerici.

## 1. Struttura e distribuzione delle classi
L’analisi preliminare ha confermato che il dataset contiene **41 variabili descrittive**, di natura eterogenea (numeriche, categoriche, contatori, frequenze), e due colonne aggiuntive:  
- `label` → etichetta multiclass che identifica traffico normale o tipologie specifiche di attacco (DoS, Probe, R2L, U2R).  
- `difficulty` → indice della complessità dell’istanza, utile per studi avanzati ma non necessario in fase di training.  

La distribuzione delle classi risulta **fortemente sbilanciata**: alcune tipologie di attacco, come *neptune* e *smurf*, sono sovrarappresentate, mentre altre, quali *spy* o *perl*, compaiono in quantità marginali.  

### Motivazione metodologica
Lo sbilanciamento è un fenomeno noto nei dataset di sicurezza informatica: gli attacchi reali seguono tipicamente una distribuzione “long tail”, dove poche famiglie sono molto diffuse e molte altre sono rare.  
In ambito di *data analysis*, è essenziale rilevare questo aspetto per evitare che i modelli di classificazione risultino **biased** verso le classi maggioritarie.  

### Scelta progettuale
In questa fase è stata introdotta un’etichetta **binaria** (`binary_label`: *normal* vs *attack*) al fine di ridurre la complessità del problema e focalizzarsi sull’obiettivo primario di un IDS: distinguere il traffico lecito da quello malevolo.  
Tale approccio consente inoltre di ottenere valutazioni più stabili, rinviando a una fase successiva l’eventuale estensione al problema **multi-classe**.

---

## 2. Statistiche descrittive delle variabili numeriche
Le statistiche di base (medie, deviazioni standard, quartili) hanno mostrato valori con range molto estesi e presenza di numerosi **outlier**. Ad esempio, feature come `src_bytes` e `dst_bytes` presentano distribuzioni altamente asimmetriche, con valori eccezionalmente elevati in corrispondenza di specifiche istanze di attacco.

### Motivazione metodologica
In un contesto di sicurezza, gli outlier non rappresentano rumore da eliminare, bensì spesso corrispondono a **pattern anomali reali** (e.g., attacchi DoS caratterizzati da volumi di traffico anomali).  
È quindi importante **preservarli** come indizi utili per la classificazione, ma al contempo ridurre gli effetti distorsivi delle scale diverse mediante tecniche di normalizzazione.

### Scelta progettuale
Si è optato per l’applicazione di uno **StandardScaler**, al fine di portare tutte le variabili numeriche su una scala comparabile (media = 0, deviazione standard = 1).  
Ciò risulta particolarmente rilevante per algoritmi basati su distanze o gradienti, come regressione logistica, SVM o reti neurali.

---

## 3. Correlazioni tra variabili
La matrice di correlazione ha evidenziato la presenza di coppie di feature altamente collegate (e.g., `serror_rate` ↔ `srv_serror_rate`, `rerror_rate` ↔ `srv_rerror_rate`).  
Questa ridondanza è tipica di dataset costruiti su metriche di rete, dove variabili derivate condividono l’informazione di base.

### Motivazione metodologica
Feature fortemente correlate possono determinare:  
- inefficienza computazionale (modelli più complessi senza reale incremento informativo);  
- rischio di *multicollinearità* in algoritmi parametrici (regressione, reti neurali), con conseguente perdita di interpretabilità.  

### Possibili miglioramenti
In prospettiva, sarà opportuno introdurre tecniche di **feature selection** (es. importanza delle feature in Random Forest, regressione L1) o **riduzione dimensionale** (es. PCA) per eliminare ridondanze preservando la capacità predittiva.

---

## 4. Preprocessing complessivo
Le operazioni di preprocessing hanno incluso:  
- encoding delle variabili categoriche (`protocol_type`, `service`, `flag`) → necessarie poiché gli algoritmi di ML richiedono input numerici;  
- encoding binario della variabile target (`normal`=0, `attack`=1);  
- standardizzazione delle variabili numeriche.  

### Motivazione metodologica
Tali trasformazioni garantiscono che il dataset sia in una forma **consistente e idonea** all’addestramento di modelli di *Machine Learning*, evitando bias legati a scale eterogenee o input non numerici.

---

# ✅ Sintesi critica
L’analisi ha evidenziato i seguenti punti chiave:
1. **Sbilanciamento marcato delle classi** → richiederà metriche adeguate (precision, recall, f1-score) e potenzialmente tecniche di riequilibrio (SMOTE, undersampling).  
2. **Outlier informativi** → non eliminati, ma trattati tramite scaling.  
3. **Ridondanza tra feature** → opportuno considerare future strategie di riduzione dimensionale.  
4. **Preprocessing coerente** → encoding e scaling hanno reso i dati utilizzabili per algoritmi ML moderni.

---

# 🔮 Prospettive di miglioramento
- **Gestione dello sbilanciamento**: impiego di tecniche di *resampling* o approcci di *cost-sensitive learning*.  
- **Analisi multi-classe**: estensione per distinguere le quattro categorie principali (DoS, Probe, R2L, U2R).  
- **Feature engineering**: creazione di variabili derivate (es. rapporti tra `src_bytes` e `dst_bytes`, frequenze normalizzate).  
- **Riduzione dimensionale**: eliminazione delle variabili fortemente correlate per migliorare robustezza ed efficienza.  

---

## 📌 Conclusione finale
Il dataset NSL-KDD, dopo la fase di analisi e preprocessing, risulta **pronto per l’addestramento di modelli di Machine Learning**.  
Le scelte metodologiche adottate (binaria vs multi-classe, preservazione outlier, scaling uniforme) sono state guidate dalla natura del problema di **Intrusion Detection**, dove l’obiettivo primario non è l’accuratezza globale, bensì la capacità di individuare **eventi rari e anomali**.  

Questo lavoro costituisce la base solida per la fase successiva: sperimentazione di algoritmi di ML, confronto delle performance e costruzione del prototipo di IDS intelligente *logAIzer*.

---------------

# 🤖 logAIzer – Modulo Machine Learning

Il modulo di Machine Learning di logAIzer implementa una pipeline per l’addestramento e la valutazione di modelli di classificazione sul dataset NSL-KDD, con l’obiettivo di sviluppare un sistema di Intrusion Detection (IDS) basato su tecniche di analisi dati e apprendimento automatico.

 # 📂 Struttura del progetto
src/
│── dataloader.py      # Caricamento e preprocessing dei dati
│── models.py          # Definizione dei modelli ML
│── train.py           # Pipeline di training e validazione
│── evaluate.py        # Metriche di valutazione e report
config.json            # File di configurazione
config_schema.json     # Schema JSON per validazione
reports/               # Output di metriche e confusion matrix


La struttura modulare rende il codice leggibile, estendibile e facilmente manutenibile, in linea con le best practice accademiche e industriali.

# ⚙️ Configurazione

Tutti i parametri sono definiti nel file config.json, validato tramite config_schema.json.
Questo approccio garantisce flessibilità e riduce la possibilità di errori manuali.

Esempio di config.json

``` json
{
  "data": {
    "train_path": "data/nsl-kdd/KDDTrain+.TXT",
    "test_path": "data/nsl-kdd/KDDTest+.TXT",
    "binary": true
  },
  "models": {
    "logistic_regression": {
      "enabled": true,
      "max_iter": 1000,
      "class_weight": "balanced",
      "solver": "lbfgs"
    },
    "random_forest": {
      "enabled": true,
      "n_estimators": 100,
      "class_weight": "balanced",
      "random_state": 42
    }
  },
  "output": {
    "reports_dir": "reports/"
  }
}
```

 # 🧩 Componenti principali
🔹 DataLoader (dataloader.py)

Carica i dataset train/test.

Esegue preprocessing:

encoding delle variabili categoriche (protocol_type, service, flag),

conversione etichetta binaria (normal = 0, attack = 1),

standardizzazione delle feature numeriche.

👉 Scopo: rendere i dati numerici e comparabili per i modelli ML.

🔹 Modelli (models.py)

Sono stati implementati due modelli baseline:

Logistic Regression → modello lineare, semplice e interpretabile.

Random Forest → modello non lineare, robusto a outlier e feature ridondanti.

Entrambi utilizzano class_weight="balanced" per gestire lo sbilanciamento delle classi.

🔹 Training (train.py)

Carica configurazione da config.json.

Esegue addestramento dei modelli abilitati.

Valuta le performance sui dati di test.

Integra il modulo evaluate.py per salvare i risultati.

🔹 Valutazione (evaluate.py)

Per ogni modello vengono generati:

Classification report (precision, recall, f1-score, support) → salvato in JSON.

Confusion matrix → salvata come PNG.

# 📊 Metriche adottate

Poiché il dataset è sbilanciato, l’accuracy non è sufficiente.
Sono state privilegiate metriche più informative per un IDS:

Precision → ridurre i falsi positivi.

Recall → intercettare il maggior numero di attacchi (falsi negativi critici).

F1-score → equilibrio tra precision e recall.

Confusion matrix → visualizzazione immediata delle performance.

# ▶️ Esecuzione

Dopo aver installato le dipendenze:

pip install -r requirements.txt


lanciare il training con:

python src/train.py --config config.json --schema config_schema.json

 #📂 Output atteso

Nella cartella reports/ vengono prodotti:

lr_report.json → metriche Logistic Regression

lr_cm.png → confusion matrix Logistic Regression

rf_report.json → metriche Random Forest

rf_cm.png → confusion matrix Random Forest

# 🧭 Considerazioni finali

La pipeline implementata è modulare, configurabile e riproducibile.

Le scelte metodologiche (binary classification, scaling uniforme, gestione sbilanciamento) sono state guidate dalle caratteristiche del dataset e dalle esigenze di un IDS reale.

Il modulo ML costituisce la base per sviluppi futuri, tra cui:

testing di modelli più avanzati (XGBoost, Reti Neurali),

applicazione di tecniche di bilanciamento (SMOTE, cost-sensitive learning),

classificazione multi-classe per distinguere le diverse famiglie di attacco,

integrazione con tecniche di early stopping e logging (TensorBoard).
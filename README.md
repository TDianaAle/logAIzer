

# Analisi Dati – NSL-KDD Dataset
 
L’attività di analisi dati condotta sul dataset **NSL-KDD** ha avuto un duplice obiettivo:  
1. fornire una comprensione approfondita della struttura e delle proprietà dei dati;  
2. individuare le criticità e le trasformazioni necessarie affinché il dataset possa essere impiegato in modo efficace in modelli di *Machine Learning* per la realizzazione di un sistema di **Intrusion Detection (IDS)**.

## ℹDocumentazione del dataset
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

# Random Forest

La Random Forest è stata impiegata per analizzare il dataset e identificare le feature più rilevanti per distinguere traffico normale da attacchi.

- Le variabili `src_bytes`, `dst_bytes`, `same_srv_rate`, `dst_host_srv_count` e `flag` si sono dimostrate tra le più discriminanti.  

- L’analisi ha evidenziato che un sottoinsieme di **15–20 feature** è sufficiente a spiegare oltre il 70% della capacità predittiva del modello.  


## 1. Struttura e distribuzione delle classi
L’analisi preliminare ha confermato che il dataset contiene **41 variabili descrittive**, di natura eterogenea (numeriche, categoriche, contatori, frequenze), e due colonne aggiuntive:  
- `label` → etichetta multiclass che identifica traffico normale o tipologie specifiche di attacco (DoS, Probe, R2L, U2R).  
- `difficulty` → indice della complessità dell’istanza, utile per studi avanzati ma non necessario in fase di training.  

La distribuzione delle classi risulta **fortemente sbilanciata**: alcune tipologie di attacco, come *neptune* e *smurf*, sono sovrarappresentate, mentre altre, quali *spy* o *perl*, compaiono in quantità marginali.  

Lo sbilanciamento è un fenomeno noto nei dataset di sicurezza informatica: gli attacchi reali seguono tipicamente una distribuzione “long tail”, dove poche famiglie sono molto diffuse e molte altre sono rare.  
In ambito di *data analysis*, è essenziale rilevare questo aspetto per evitare che i modelli di classificazione risultino **biased** verso le classi maggioritarie.  

In questa fase è stata introdotta un’etichetta **binaria** (`binary_label`: *normal* vs *attack*) al fine di ridurre la complessità del problema e focalizzarsi sull’obiettivo primario di un IDS: distinguere il traffico lecito da quello malevolo.  
Tale approccio consente inoltre di ottenere valutazioni più stabili, rinviando a una fase successiva l’eventuale estensione al problema **multi-classe**.

---

## 2. Statistiche descrittive delle variabili numeriche
Le statistiche di base (medie, deviazioni standard, quartili) hanno mostrato valori con range molto estesi e presenza di numerosi **outlier**. Ad esempio, feature come `src_bytes` e `dst_bytes` presentano distribuzioni altamente asimmetriche, con valori eccezionalmente elevati in corrispondenza di specifiche istanze di attacco.

In un contesto di sicurezza, gli outlier non rappresentano rumore da eliminare, bensì spesso corrispondono a **pattern anomali reali** (e.g., attacchi DoS caratterizzati da volumi di traffico anomali).  
È quindi importante **preservarli** come indizi utili per la classificazione, ma al contempo ridurre gli effetti distorsivi delle scale diverse mediante tecniche di normalizzazione.

### Soluzione
Si è optato per l’applicazione di uno **StandardScaler**, al fine di portare tutte le variabili numeriche su una scala comparabile (media = 0, deviazione standard = 1).  
Ciò risulta particolarmente rilevante per algoritmi basati su distanze o gradienti, come regressione logistica, SVM o reti neurali.

---

## 3. Correlazioni tra variabili
La matrice di correlazione ha evidenziato la presenza di coppie di feature altamente collegate (e.g., `serror_rate` ↔ `srv_serror_rate`, `rerror_rate` ↔ `srv_rerror_rate`).  
Questa ridondanza è tipica di dataset costruiti su metriche di rete, dove variabili derivate condividono l’informazione di base.

Feature fortemente correlate possono determinare:  
- inefficienza computazionale (modelli più complessi senza reale incremento informativo);  
- rischio di *multicollinearità* in algoritmi parametrici (regressione, reti neurali), con conseguente perdita di interpretabilità.  

---
## 4. ## Feature Selection con Random Forest

Per ridurre la ridondanza e identificare le variabili più rilevanti ai fini della classificazione, è stata applicata una **Feature Selection basata su Random Forest**.  
Questa tecnica sfrutta l’importanza delle variabili (`feature importance`), calcolata come riduzione media dell’impurità ottenuta quando una feature viene utilizzata per effettuare split all’interno degli alberi.

### Risultati principali
- Le feature **più importanti** risultano essere `src_bytes`, `dst_bytes`, `same_srv_rate`, `dst_host_srv_count`, `dst_host_same_srv_rate` e `flag`.  
  Queste variabili descrivono la quantità di traffico scambiato e le caratteristiche delle connessioni TCP/servizi, elementi chiave per individuare anomalie.  
- Alcune feature, come `num_outbound_cmds`, `is_host_login` e `su_attempted`, hanno importanza trascurabile (< 0.001), indicando che possono essere eliminate senza perdita di accuratezza.  
- La **curva cumulativa** mostra che le prime ~15–20 feature spiegano già oltre il **70–80% dell’importanza totale**, suggerendo che un sottoinsieme ristretto di variabili è sufficiente a mantenere buone performance del modello. 

---

## 5. Preprocessing
Le operazioni di preprocessing hanno incluso:  
- encoding delle variabili categoriche (`protocol_type`, `service`, `flag`) → necessarie poiché gli algoritmi di ML richiedono input numerici;  
- encoding binario della variabile target (`normal`=0, `attack`=1);  
- standardizzazione delle variabili numeriche.  

### Motivazione metodologica
Tali trasformazioni garantiscono che il dataset sia in una forma **consistente e idonea** all’addestramento di modelli di *Machine Learning*, evitando bias legati a scale eterogenee o input non numerici.

---


##  Conclusione finale
Il dataset NSL-KDD, dopo la fase di analisi e preprocessing, risulta **pronto per l’addestramento di modelli di Machine Learning**.  
Le scelte metodologiche adottate (binaria vs multi-classe, preservazione outlier, scaling uniforme) sono state guidate dalla natura del problema di **Intrusion Detection**, dove l’obiettivo primario non è l’accuratezza globale, bensì la capacità di individuare **eventi rari e anomali**.  

---------------

#  logAIzer – Modulo Machine Learning

Il modulo di Machine Learning di logAIzer implementa una pipeline per l’addestramento e la valutazione di modelli di classificazione sul dataset NSL-KDD, con l’obiettivo di sviluppare un sistema di Intrusion Detection (IDS) basato su tecniche di analisi dati e apprendimento automatico.

 #  Struttura del progetto
src/
│── dataloader.py # Caricamento, preprocessing e scaling dei dati
│── models.py # Definizione e ottimizzazione dei modelli ML
│── train.py # Pipeline di training, validazione e salvataggio
│── inference.py # Predizioni su nuovi campioni
config.json # File di configurazione
config_schema.json # Schema JSON per validazione
reports/ # Output di metriche, modelli e confusion matrix

# Artificial Intelligence & Machine Learning

## 🚀 Come avviare l’IDS

Il progetto è strutturato in due fasi principali:

1. **Preparazione e training del modello** (offline, con i file in `src/` e il dataset NSL-KDD).  
2. **Rilevamento in tempo reale** (online, con `packet_sniffer.py`).  

---

### 1️⃣ Fase offline – Analisi dati e Machine Learning

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
    Definisce i modelli ML (es. Random Forest, Logistic Regression).

  - `train.py`  
    Script principale di training.  
    - Carica i dati dal `dataloader`.  
    - Applica encoding e scaling.  
    - Addestra i modelli definiti in `models.py`.  
    - Salva il modello addestrato in `reports/random_forest_model.joblib`.

  - `inference.py`  
    Permette di testare un modello già addestrato su nuovi dati (es. sul test set NSL-KDD).  

👉 **Ordine di esecuzione tipico (fase offline):**

```bash
# 1. Carica e analizza i dati (facoltativo, solo per EDA)
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

Tale scelta risponde alla necessità didattica di semplificare la pipeline di training e garantire risultati chiari nella fase di dimostrazione.

---

## 3. Preprocessing dei dati
### 3.1 Encoding delle variabili categoriche
Le variabili `protocol_type`, `service` e `flag` sono state trattate con **Label Encoding**, trasformandole da stringhe a rappresentazioni numeriche. La scelta è motivata dal fatto che il Random Forest non richiede feature numeriche scalate su range specifici, ma necessita di un mapping consistente tra training e runtime.  
Per garantire consistenza, gli encoder addestrati sono stati **serializzati in un file unico (`encoders.joblib`)**, così da poter essere riutilizzati in fase di sniffing in tempo reale.

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

### IDS con Scapy basato su ML
### Implementazione tecnica

La fase di rilevamento in tempo reale è stata implementata nello script `packet_sniffer.py`, il quale si basa sulla libreria **Scapy**, un framework Python per la manipolazione e l’analisi del traffico di rete.  

 Scapy consente di:
- sniffare pacchetti direttamente dall’interfaccia di rete, senza dipendere da applicazioni esterne,  
- accedere a tutti i campi dei protocolli (IP, TCP, UDP, flag, lunghezza, porte, ecc.),  
- manipolare e ricostruire pacchetti, caratteristica utile in un contesto di simulazione di attacchi,  
- integrarsi facilmente con Python e con i modelli di Machine Learning precedentemente addestrati.  

Dal punto di vista concettuale, un IDS deve avere la capacità di:
1. **ispezionare il traffico di rete**,  
2. **estrarre feature significative**,  
3. **classificare o correlare** tali feature con un modello di detection.  

Scapy fornisce quindi il livello di “packet capture” e parsing, ossia la componente di basso livello che, in un IDS reale (come Snort o Suricata), sarebbe svolta dal motore di cattura. Nel nostro caso, Scapy rappresenta il **collegamento tra il traffico reale** e la pipeline di Machine Learning addestrata sul dataset NSL-KDD.

---

#### Estrazione delle feature
Dopo aver catturato i pacchetti, lo script ricostruisce **le stesse 20 feature selezionate dal dataset NSL-KDD**, garantendo coerenza con la fase di training.  
Esempi:  
- **Contatori di byte**: `src_bytes`, `dst_bytes`, ottenuti sommando i byte inviati per ogni connessione.  
- **Conteggi su finestre mobili**: `count` e `srv_count`, che misurano la frequenza di connessioni per IP sorgente o per porta di destinazione in una finestra temporale.  
- **Tassi di servizio**: `same_srv_rate`, `diff_srv_rate`, che indicano la percentuale di pacchetti diretti allo stesso servizio rispetto al traffico totale osservato.  
- **Flag TCP**: i valori grezzi di Scapy (`A`, `PA`, `R`, ecc.) vengono mappati nelle categorie NSL-KDD (`SF`, `S0`, `REJ`, ecc.) per mantenere compatibilità con il dataset di training.  
- **Protocollo**: la feature `protocol_type` viene derivata distinguendo tra `tcp` e `udp`.  
- **Service**: non essendo disponibili i servizi applicativi reali, si utilizza la **porta di destinazione** come proxy della feature `service` del dataset NSL-KDD.  

---

#### Feature non calcolabili in tempo reale
Alcune variabili presenti nel dataset NSL-KDD, come `serror_rate` o `rerror_rate`, non sono direttamente osservabili tramite sniffing passivo:
- derivano da log di sistema o da conoscenza dello stato della sessione TCP,  
- richiedono un’analisi lato server (es. errori nella risposta), che non può essere dedotta con certezza solo dal traffico catturato passivamente.  

Per queste variabili, nello script vengono utilizzati valori placeholder (`0.0`). Questa scelta, pur riducendo la fedeltà rispetto al dataset originale, è metodologicamente accettabile in quanto:
1. garantisce la **consistenza dimensionale** delle feature,  
2. preserva l’ordine delle variabili atteso dal modello,  
3. mostra concretamente il **gap tra dataset simulati e traffico reale**.

---
 Questa architettura permette di applicare il modello addestrato offline al traffico osservato in tempo reale, realizzando un IDS funzionante in ambiente di laboratorio.

## DEMO
Per la dimostrazione pratica dell’IDS è stato scritto uno script che simula traffico anomalo e il sistema IDS lo intercetta in tempo reale:

 `evil_script.py` (TCP flood/brute-force) che
- Genera ~20–50 connessioni TCP al secondo verso un server target (es. `localhost:8080`).  
- Invia richieste HTTP sintetiche.  
- Effetto: incremento rapido di `srv_count` e `same_srv_rate`, tipico di un brute-force o attacco DoS.

⚠️ ATTENZIONE⚠️
Lo script deve essere testato
 ️️**esclusivamente su macchine di test controllate**, poiché genera traffico potenzialmente destabilizzante.

---

## 7. Analisi e visualizzazione
È stato sviluppato lo script `captured_packet_analyzer.py`, che elabora i log generati (`captured_packets.csv`) e produce grafici descrittivi:  
- **Distribuzione pacchetti** (normal vs attack), utile a quantificare l’impatto di un attacco.  
- **Timeline dei pacchetti** raggruppati per secondo, che evidenzia i picchi durante flood o brute-force.  

---

### Conclusioni
- **necessità di consistenza nel preprocessing**: encoder e scaler del training sono stati riutilizzati in runtime.  
- **gap tra dataset simulati e traffico reale**: non tutte le feature sono direttamente calcolabili → introduzione di euristiche.  
- approccio **ibrido (ML + rule-based)**, in linea con le tendenze moderne in IDS.  
- il dataset NSL-KDD, pur utile in ambito accademico, non riflette fedelmente la complessità del traffico moderno.  
- alcune feature sono state sostituite con proxy o placeholder, riducendo la fedeltà.  
-**estensioni possibili** 
- implementazione di una pipeline completa con **SIEM** o dashboard interattiva.  
- estensione della classificazione da binaria a multiclasse, per distinguere tipologie di attacco.  
- introduzione di tecniche di **Deep Learning** (es. LSTM per analisi sequenziale).  

---

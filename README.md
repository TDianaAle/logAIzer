# 📊 Analisi Dati – NSL-KDD Dataset

L’attività di analisi esplorativa condotta sul dataset **NSL-KDD** ha avuto un duplice obiettivo:  
1. fornire una comprensione approfondita della struttura e delle proprietà dei dati;  
2. individuare le criticità e le trasformazioni necessarie affinché il dataset possa essere impiegato in modo efficace in modelli di *Machine Learning* per la realizzazione di un sistema di **Intrusion Detection (IDS)**.

---

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

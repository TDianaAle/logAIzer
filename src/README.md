## logAIzer – Modulo Artificial Intelligence & Machine Learning

# Introduzione e Obiettivo

Il modulo di Machine Learning di logAIzer implementa una pipeline completa per l’addestramento, la valutazione e l’inferenza di modelli di classificazione sul dataset NSL-KDD, con l’obiettivo di sviluppare un Intrusion Detection System (IDS) in grado di distinguere traffico di rete legittimo da potenziale traffico anomalo.

La progettazione si fonda sui risultati della fase di Analisi Dati (EDA), che ha permesso di evidenziare criticità del dataset (squilibrio di classe, ridondanza di variabili, necessità di encoding e normalizzazione).


Il training è stato condotto utilizzando un sottoinsieme delle feature più informative, selezionate in base alla loro rilevanza, con un’attenzione particolare a quelle che possono essere calcolate e osservate in tempo reale durante il monitoraggio della rete.
In particolare, il modello è stato addestrato su variabili in grado di catturare fenomeni caratteristici di tre famiglie di attacco comuni:

- Probe (port scanning, es. scansioni con Nmap o Nuclei)
Questi attacchi si distinguono perché generano un numero elevato di connessioni brevi e ripetute verso host o porte diverse.

Feature chiave: count, srv_count, diff_srv_rate, dst_host_srv_count, same_srv_rate.

Queste variabili descrivono quante connessioni recenti sono state fatte verso lo stesso host o servizio e con quale varietà.

Un probe produce tipicamente valori anomali di varietà elevata (molti servizi diversi in poco tempo).

- Brute forcing (es. tentativi ripetuti di login)
Qui il tratto distintivo è l’elevato numero di connessioni fallite in breve tempo verso un servizio di autenticazione.

Feature chiave: num_failed_logins, logged_in, hot.

Un brute force genera una sequenza di tentativi con num_failed_logins elevato e stato logged_in=0.

Il modello impara che questa combinazione è fortemente associata a traffico malevolo.

- TCP Flood (es. SYN flood, traffico DoS)
Si tratta di attacchi basati su grandi volumi di pacchetti inviati in rapida successione, spesso incompleti o con flag sospetti.

Feature chiave: src_bytes, dst_bytes, serror_rate, srv_serror_rate, dst_host_serror_rate.

Un flood si riconosce perché i byte inviati/ricevuti sono molto sbilanciati e i tassi di errore (serror_rate) si avvicinano a 1.

Il modello sfrutta queste anomalie per distinguere un flood dal traffico legittimo.

## Come riesce il modello a riconoscerli?

Il modello utilizzato è una rete neurale multilayer perceptron (MLP) che riceve in input i valori numerici delle feature selezionate.

Durante il training, la rete “vede” migliaia di esempi di traffico normale e attacchi (descritti sopra)

Ogni epoca di addestramento aggiorna i pesi della rete in modo da ridurre la loss di classificazione e col tempo, la rete impara pattern ricorrenti.

In pratica, il modello non ha una regola scritta a mano(euristica), ma costruisce internamente rappresentazioni non lineari che separano bene lo spazio dei dati “normali” da quello “anomalo”.
Questo è possibile perché le feature scelte catturano proprio le caratteristiche operative degli attacchi: frequenza, varietà, volumi, errori.

## Architettura scelta: Multilayer Perceptron (MLP)

Il progetto utilizza un MLP, rete neurale feed-forward adatta a dati tabellari come quelli del dataset scelto. L’architettura prevede:

- Input layer con dimensione pari al numero di feature selezionate.

- Hidden layers fully connected con attivazioni ReLU, per apprendere relazioni non lineari; 
- Output layer con 2 neuroni e softmax per classificare normal vs attack.

**la scelta dei layer hidden e della dimensione dei neuroni è stata fatta per mantenere un buon compromesso tra capacità predittiva e leggerezza computazionale, poiché il sistema deve funzionare in tempo reale**

L’MLP è stato implementato nel file **src/torch_models.py** tramite la classe MLPClassifier e addestrato in **src/torch_train.py** usando Adam, CrossEntropyLoss, DataLoader per batch e early stopping.

**MLP minimizza la CrossEntropyLoss e che le rappresentazioni apprese nello spazio latente permettono di separare regioni di decisione tra traffico normale e anomalo**.

Il modello migliore viene salvato in **../reports/model_best.pth** e utilizzato in **src/inference_torch.py** dalla funzione predict(sample), che restituisce la classe del traffico preprocessato.

La scelta dell’MLP è motivata dalla natura tabellare e ibrida (numerico + categorico) dei dati, dall’esigenza di un modello leggero ed efficiente in tempo reale, e dalla sua capacità di catturare pattern non lineari tipici di attacchi come probe, brute force e DoS flood.

## moduli

# src/

**dataloader.py**

- Carica il dataset NSL-KDD e assegna manualmente i nomi delle colonne.

- Converte la label multiclass in una variabile binaria (normal=0, attack=1).

- Applica Label Encoding alle variabili categoriche (protocol_type, service,    flag), salvando gli encoder in **../reports/encoders.joblib** per garantire consistenza in fase di inferenza.

- Normalizza le feature numeriche con StandardScaler, salvato in **../reports/scaler.joblib**.

- Restituisce X_train, y_train, X_test, y_test pronti per l’addestramento.

**feature_selection.py**

- Applica un Random Forest Classifier per calcolare l’importanza delle variabili.

- Produce un file **../reports/feature_importance.csv** che ordina le feature per rilevanza.

- Consente di addestrare i modelli solo sulle top-k variabili, riducendo la dimensionalità senza sacrificare accuratezza.

**torch_models.py**

- Definisce l’architettura di un Multilayer Perceptron (MLP) con PyTorch.

- L’MLP utilizza layer fully-connected con funzioni di attivazione ReLU e un livello finale di output per la classificazione binaria.

- Costituisce il cuore predittivo dell’IDS.

**torch_train.py**

- Implementa il ciclo di training della rete neurale.

- Gestisce i DataLoader per batch, la loss function (CrossEntropyLoss), l’ottimizzatore (Adam) e il monitoraggio delle metriche.

- Integra Early Stopping per interrompere l’addestramento in caso di overfitting.

- Salva il modello migliore in **../reports/model_best.pth** e l’ultimo modello in **../reports/model_last.pth**.

- Utilizza TensorBoard per registrare loss e accuratezza durante le epoche di training.

**inference_torch.py**

- Permette di utilizzare il modello addestrato in fase di rilevamento.

- Carica il file model_best.pth, insieme agli encoder e scaler salvati.

- Espone una funzione predict(sample) che riceve in input un dizionario con tutte le 41 feature originali del dataset e restituisce una predizione binaria (normal o attack).

- Garantisce coerenza totale con il preprocessing applicato durante l’addestramento.



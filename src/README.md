## logAIzer – Modulo AI & ML

Avvio:
1. Installare le dipendenze:
```python
pip install -r requirements.txt
```

oppure creare l’ambiente Conda:
```python
conda env create -f environment.yaml
conda activate logaizer
```
2. Addestrare il modello:
```python
python src/torch_train.py
```
3. Eseguire l’inferenza su un campione:
```python
python src/inference_torch.py
```
---
# Introduzione e Obiettivo

Il modulo di Machine Learning di logAIzer implementa una pipeline completa per l’addestramento, la valutazione e l’inferenza di modelli di classificazione sul dataset NSL-KDD, con l’obiettivo di sviluppare un Intrusion Detection System (IDS) in grado di distinguere traffico di rete legittimo da potenziale traffico anomalo.

La progettazione si fonda sui risultati della fase di Analisi Dati (EDA), che ha permesso di evidenziare criticità del dataset (squilibrio di classe, ridondanza di variabili, necessità di encoding e normalizzazione). In questa fase è stata condotta anche una feature selection basata su Random Forest, che ha permesso di ordinare le variabili per importanza predittiva.

Sulla base di questi risultati, per l’addestramento finale è stato scelto di utilizzare le 8 feature più rilevanti, poiché hanno mostrato di spiegare la maggior parte della capacità discriminante del dataset e possono essere calcolate in tempo reale durante il monitoraggio della rete.

---
# Attacchi e feature rilevanti

Il modello è stato addestrato concentrandosi su variabili capaci di catturare fenomeni caratteristici di tre famiglie di attacco comuni:

- Probe (port scanning, es. Nmap o Nuclei)
Attacchi che generano numerose connessioni brevi e ripetute verso host o porte diverse.
Feature chiave: count, srv_count, diff_srv_rate, dst_host_srv_count, same_srv_rate.
→ Un probe produce valori anomali di varietà elevata, con molte richieste diverse in poco tempo.

- Brute forcing (tentativi ripetuti di login)
Riconoscibili per l’alto numero di connessioni fallite verso un servizio di autenticazione.
Feature chiave: num_failed_logins, logged_in, hot.
→ Una sequenza di tentativi falliti con num_failed_logins alto e logged_in=0 è tipicamente malevola.

- TCP Flood (es. SYN flood, traffico DoS)
Basati su volumi elevati di pacchetti inviati rapidamente, spesso incompleti o con flag sospetti.
Feature chiave: src_bytes, dst_bytes, serror_rate, srv_serror_rate, dst_host_serror_rate.
→ Un flood si riconosce da sbilanciamenti estremi nei byte inviati/ricevuti e da tassi di errore vicini a 1.
---
# Come riesce il modello a riconoscerli?
# Architettura scelta: Multilayer Perceptron (MLP)

Il modello utilizza come architettura una rete neurale Multilayer Perceptron (MLP) che riceve in input i valori numerici delle feature selezionate.
Durante il training, la rete viene esposta a migliaia di esempi di traffico normale e attacchi: a ogni epoca, i pesi interni vengono aggiornati per ridurre la loss di classificazione.

In questo modo, l’MLP non applica regole scritte a mano, ma costruisce internamente rappresentazioni non lineari che separano lo spazio dei dati “normali” da quello “anomalo”.
Le feature scelte catturano i segnali operativi chiave (frequenza, varietà, volumi, errori), rendendo possibile questa separazione.

Input layer: dimensione pari al numero di feature selezionate.

Hidden layers: fully connected con attivazioni ReLU, per apprendere relazioni non lineari.

Output layer: 2 neuroni con softmax per classificare normal vs attack.

**La scelta delle dimensioni è stata fatta per mantenere un buon compromesso tra capacità predittiva ed efficienza computazionale, requisito fondamentale in uno scenario IDS real-time.**

L’MLP è stato implementato in **src/torch_models.py** (classe MLPClassifier) e addestrato in **src/torch_train.py** con ottimizzatore Adam, loss function CrossEntropyLoss, DataLoader per batch ed early stopping.

Il modello migliore viene salvato in **reports/model_best.pth** e utilizzato in **src/inference_torch.py**, dove la funzione predict(sample) restituisce la classe del traffico preprocessato.

---

 # Moduli

**dataloader.py**

- In questo caso non carica più il dataset completo ma solo le top 8 features selezionate dopo la fase di feature importance nell'EDA, assegnando manualmente i nomi delle colonne.

 - Converte la label multiclass in una variabile binaria (normal=0, attack=1).
  - Applica Label Encoding alle variabili categoriche (protocol_type, service, flag), salvando gli encoder in **../reports/encoders.joblib** per garantire consistenza in fase di inferenza. 

  - Normalizza le feature numeriche con StandardScaler, salvato in **../reports/scaler.joblib**. 
  
  - Restituisce X_train, y_train, X_test, y_test pronti per l’addestramento. 

---

**torch_models.py**

-  Funzione che riceve in ingresso un vettore di 8 feature numeriche, selezionate come le più rilevanti per la discriminazione normale o attacco.

- Ciascun layer nascosto applica una trasformazione lineare seguita da una funzione di attivazione ReLU, che introduce non-linearità e consente di apprendere relazioni complesse tra le variabili.

- I layer successivi raffinano progressivamente queste rappresentazioni, riducendo rumore e amplificando i pattern più significativi per la classificazione.

- Lo strato di output produce due valori (logit), corrispondenti alle due classi possibili: normal e attack.

- I logit vengono trasformati tramite softmax in una distribuzione di probabilità normalizzata, tale che la somma sia pari a 1.

- La decisione finale si ottiene scegliendo la classe con probabilità maggiore, permettendo così al sistema di classificare automaticamente ogni campione di traffico in base alla sua somiglianza con i pattern osservati in fase di addestramento.

---

 # Schema

            Input Layer (8 feature)
      ┌──────────────────────────────────┐
      │ duration, src_bytes, dst_bytes,  │
      │ same_srv_rate, diff_srv_rate,    │
      │ count, dst_host_srv_count, flag  │
      └──────────────────────────────────┘
                       │
                       ▼
           Hidden Layer 1 (64 neuroni)
      ┌──────────────────────────────────┐
      │ Linear(8 → 64)                   │
      │ ReLU activation                  │
      │ Dropout(0.3)                     │
      └──────────────────────────────────┘
                       │
                       ▼
           Hidden Layer 2 (64 neuroni)
      ┌──────────────────────────────────┐
      │ Linear(64 → 64)                  │
      │ ReLU activation                  │
      │ Dropout(0.3)                     │
      └──────────────────────────────────┘
                       │
                       ▼
             Output Layer (2 neuroni)
      ┌──────────────────────────────────┐
      │ Linear(64 → 2)                   │
      │ Softmax → Probabilità            │
      │  - Classe 0: Normal              │
      │  - Classe 1: Attack              │
      └──────────────────────────────────┘

---

**torch_train.py**

- Implementa il ciclo di training della rete neurale.

- Gestisce i DataLoader per batch, la loss function (nn.CrossEntropyLoss), l’ottimizzatore (optim.Adam) e il monitoraggio delle metriche.

- Integra Early Stopping per interrompere l’addestramento in caso di overfitting.

- Salva il modello migliore in ../reports/model_best.pth e l’ultimo modello in ../reports/model_last.pth tramite torch.save.

-  TensorBoard (torch.utils.tensorboard.SummaryWriter) per registrare loss e accuratezza durante le epoche di training.

- Sfrutta in maniera estesa le classi e le funzioni native di PyTorch, come torch.Tensor, TensorDataset, DataLoader, e i moduli di rete (nn.Module, nn.Linear, nn.ReLU, nn.Dropout) che costituiscono l’ossatura dell’intero processo di training.

-----
               Dataloader (8 feature selezionate)
                   │
                   ▼
          Train / Test Dataset (X, y)
                   │
                   ▼
        ┌───────────────────────────────┐
        │   Conversione in Tensori      │
        │   e DataLoader per batch      │
        └───────────────────────────────┘
                   │
                   ▼
         ┌────────────────────────────┐
         │   MLPClassifier (8→64→64→2)│
         │   Loss: CrossEntropyLoss   │
         │   Optimizer: Adam          │
         └────────────────────────────┘
                   │
   ┌───────────────┴───────────────┐
   ▼                               ▼
Training Loop                Validazione Loop
(Forward, Backward, Update)  (Calcolo Loss + Accuracy)
   │                               │
   └───────────────┬───────────────┘
                   ▼
        Early Stopping & Saving
        - model_last.pth
        - model_best.pth


---

**inference_torch.py**

- Permette di utilizzare il modello addestrato in fase di rilevamento. 
- Carica il file model_best.pth, insieme agli encoder e scaler salvati. 
- Espone una funzione predict(sample) che riceve in input un dizionario con le 8 feature originali selezionate in precedenza e restituisce una predizione binaria.
----
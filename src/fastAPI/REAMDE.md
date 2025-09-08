#  Backend & Frontend – LogAIzer IDS

##  Panoramica
Il modulo `src/fastAPI/` contiene sia il **backend** (FastAPI) sia il **frontend** (Streamlit) del sistema Logaizer.  
Questi due componenti permettono di simulare pacchetti di rete, classificarli come `normal` o `attack` e visualizzare i risultati in una dashboard interattiva.

---

#  Backend – FastAPI

Il backend è sviluppato in **FastAPI** e ha le seguenti funzioni:

- Preprocessare pacchetti simulati ricevuti in formato JSON.  
- Interagire con il modello di machine learning (`MLPClassifier`).  
- Restituire la predizione (`normal` o `attack`).  
- Salvare i risultati in un database locale SQLite.  

---

##  Architettura
1. **Caricamento del modello**
   - Modello `MLPClassifier` addestrato in PyTorch.
   - File caricati:
     - `reports/model_best.pth` → pesi ottimali.
     - `reports/encoders.joblib` → codificatori delle variabili categoriche.
     - `reports/scaler.joblib` → scaler per le feature numeriche.

2. **Preprocessing dei dati**
   - Conversione delle richieste JSON in un vettore numerico coerente con il training.
   - Encoding delle feature categoriche (`protocol_type`, `service`, `flag`).
   - Inserimento automatico di feature mancanti e standardizzazione delle variabili numeriche.

3. **Predizione**
   - Output binario:
     - `normal (0)` → traffico legittimo.
     - `attack (1)` → traffico anomalo.

4. **Persistenza in database**
   - Database SQLite con tabella `events`, schema:

     ```sql
     id | ip | protocol | service | flag |
     src_bytes | dst_bytes | same_srv_rate | dst_host_srv_count |
     dst_host_same_srv_rate | logged_in | diff_srv_rate |
     prediction | details | timestamp
     ```

---

##  API

### POST `/predict`:
 riceve un pacchetto simulato e restituisce la classificazione.
- **Input (JSON):**
  ```json
  {
    "ip": "192.168.1.10",
    "protocol": "tcp",
    "service": "http",
    "flag": "SF",
    "src_bytes": 100,
    "dst_bytes": 200,
    "same_srv_rate": 1.0,
    "dst_host_srv_count": 255,
    "dst_host_same_srv_rate": 1.0,
    "logged_in": 1,
    "diff_srv_rate": 0.0
  }

### GET /logs:
restituisce la cronologia delle predizioni archiviate.

```json
[
  {
    "timestamp": "2025-09-08 12:34:56",
    "ip": "192.168.1.10",
    "prediction": "attack",
    "details": "Predizione con modello ML addestrato (MLPClassifier)"
  }
]
```
---
## Frontend – Streamlit

Il frontend è sviluppato in Streamlit e costituisce l’interfaccia interattiva del sistema.
Permette all’utente di:

- Inserire pacchetti simulati tramite form.

- Consultare la legenda delle feature per scenari tipici (Normale, TCP Flood, Brute Force, Probe).

- Visualizzare la classificazione del modello in tempo reale.

- Visualizzare cronologia degli eventi e a statistiche aggregate.
---
# Architettura

**Campi disponibili:**

Feature: src_bytes, dst_bytes, same_srv_rate, dst_host_srv_count,
dst_host_same_srv_rate, logged_in, diff_srv_rate, flag.

**Metadati: protocol, service, ip.**

Una volta compilata, la form invia i dati al backend tramite API /predict.

**Predizione in tempo reale:**

La dashboard mostra il risultato (normal / attack) subito dopo la risposta dal backend.

**Log e statistiche**

Interroga l’API /logs per mostrare la cronologia degli eventi classificati (timestamp, IP, risultato) e grafico a barre con la distribuzione tra traffico normale e attacchi.
LogAIzer – Intrusion Detection System (IDS)
# Panoramica

Sistema di Intrusion Detection (IDS) basato su Machine Learning, allenato sul dataset NSL-KDD con integrazione un backend con FastAPI e Frontend con Streamlit per facilitare la simulazione.
---
ℹ️ Nota importante

La simulazione di attacchi è puramente virtuale.
I pacchetti non vengono trasmessi sulla rete reale, ma inviati come JSON al backend e classificati dal modello ML.
---

**Per da documentazione completa di ogni fase, fare riferimento ai relativi README.md.**

data_analysis/ → esplorazione dati (README.md, analysis.ipynb)

src/ → codice sorgente (training, modelli, README.md)

reports/ → risultati, feature importance, modelli, scaler/encoder

src/fastAPI/ → demo finale (backend, dashboard, sqlite db, README.md)
---
Come funziona:

Il nucleo predittivo è costituito da un modello MLPClassifier implementato in PyTorch, addestrato utilizzando le otto feature più rilevanti individuate tramite analisi di importanza.
Queste feature consentono di distinguere il traffico normale da tre tipologie principali di anomalie di rete.

Il modello riesce a predire correttamente la natura del traffico poiché, durante l’addestramento, ha appreso i pattern numerici caratteristici associati a ciascuna classe.
In particolare, per ogni tipologia di attacco ha identificato le combinazioni di valori che lo contraddistinguono nel dataset, rendendo possibile una classificazione affidabile.

---

 Workflow completo

Clonare il repository:
```bash
git clone https://github.com/TDianaAle/logAIzer.git
```
 scarica le dipendenze:

```python

cd logaizer
pip install -r requirements.txt
```

Avviare il training:
```python
cd logaizer
python -m src.torch_train
```

Il training genera:

reports/model_best.pth

reports/encoders.joblib

reports/scaler.joblib
---
Avvio backend
```python
python -m uvicorn src.fastAPI.ids_backend:app --reload --host 127.0.0.1 --port 8000
```

In un altro terminale avviare la dashboard:
```python
python -m streamlit run src/fastAPI/ids_dashboard.py
```
---
![esempio dashboard](demo.png)
---
Nella dashboard vi è presente una legenda con i valori numerici di ogni feature per poter determinare 3 tipi di attacco e traffico normale. La legenda aiuta a compilare il form, dove si inseriscono i valori di un pacchetto ( seguendo la legenda poiché il modello riconosce quelli).

In seguito il pacchetto viene inviato al backend, che restituisce la predizione (normal o attack) e genera log con la conologia delle predizioni e un grafico con statistiche.
 ---
 

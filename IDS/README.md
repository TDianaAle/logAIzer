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

## DEMO
Per la dimostrazione pratica dell’IDS è stato scritto uno script che simula traffico anomalo e il sistema IDS lo intercetta in tempo reale:

 `evil_script.py` (TCP flood/brute-force) che
- Genera ~20–50 connessioni TCP al secondo verso un server target (es. `localhost:8080`).  
- Invia richieste HTTP sintetiche.  
- Effetto: incremento rapido di `srv_count` e `same_srv_rate`, tipico di un brute-force o attacco DoS.

⚠️ ATTENZIONE⚠️
Lo script non destabilizzerà il traffico, l'IDS lo riconosce grazie ad una regola euristica impostata es. Attack solo > 20 req/s.

## come avviarlo

aprire tre terminali diversi:

- nel primo avviare il comando per aprire un server in localhost 
```python
cd IDS
python -m http.server 8000
```
- nel secondo terminale avviare packet_sniffer.py
```python
cd IDS
python packet_sniffer.py
```
- infine, nel terzo terminale avviare evil_script.py
```
cd IDS
python evil_script.py
```

## 7. Analisi e visualizzazione
È stato sviluppato lo script `captured_packet_analyzer.py`, che elabora i log generati (`captured_packets.csv`) e produce grafici descrittivi:  
- **Distribuzione pacchetti** (normal vs attack), utile a quantificare l’impatto di un attacco.  
- **Timeline dei pacchetti** raggruppati per secondo, che evidenzia i picchi durante flood o brute-force.  

---

### Conclusioni
- **necessità di consistenza nel preprocessing**: encoder e scaler del training sono stati riutilizzati in runtime.  
- **gap tra dataset simulati e traffico reale**: non tutte le feature sono direttamente calcolabili per cui necessaria introduzione di euristiche.  

---

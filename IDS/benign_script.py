import requests
import time

URL = "http://localhost:5173"  # Skiddies in questo caso
print("[INFO] Simulazione traffico benigno...")

for i in range(10):
    try:
        r = requests.get(URL)
        print(f"[OK] Richiesta {i+1}: {r.status_code}")
    except Exception as e:
        print(f"[ERRORE] {e}")
    time.sleep(1)  # aspetta 1 secondo tra le richieste

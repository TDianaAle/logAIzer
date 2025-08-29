import requests
import time

URL = "http://localhost:5173/login" 
print("[INFO] Simulazione attacco brute force login...")

# simula un brute-force per demo
for i in range(30):
    data = {
        "username": "admin",
        "password": f"wrongpass{i}"
    }
    try:
        r = requests.post(URL, data=data)
        print(f"[!] Tentativo {i+1} inviato - Status {r.status_code}")
    except Exception as e:
        print(f"[ERRORE] {e}")
    time.sleep(0.2)  # molto più veloce per simulare un attacco

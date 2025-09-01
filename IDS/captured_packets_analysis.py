import pandas as pd
import matplotlib.pyplot as plt

CSV_PATH = "./reports/captured_packets.csv"

def main():
    # Carica i dati
    df = pd.read_csv(CSV_PATH)

    # Controlla che ci siano i dati
    if df.empty:
        print("[ERRORE] Il file CSV è vuoto.")
        return

    # === Conteggio Normal vs Attacco ===
    counts = df["prediction"].value_counts()

    plt.figure(figsize=(6,4))
    counts.plot(kind="bar", color=["green", "red"])
    plt.title("Distribuzione pacchetti (Normal vs Attacco)")
    plt.xlabel("Classe")
    plt.ylabel("Numero di pacchetti")
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig("./reports/prediction_distribution.png")
    plt.show()

    # === Attacchi nel tempo ===
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    timeline = df.groupby([pd.Grouper(key="timestamp", freq="1S"), "prediction"]).size().unstack(fill_value=0)

    plt.figure(figsize=(10,5))
    plt.plot(timeline.index, timeline.get("normal", 0), label="Normal", color="green")
    if "possibile attacco rilevato" in timeline.columns or "possibile attacco rilevato (euristica)" in timeline.columns:
        for col in timeline.columns:
            if "attacco" in col:
                plt.plot(timeline.index, timeline[col], label=col, color="red")
    plt.title("Pacchetti nel tempo")
    plt.xlabel("Tempo (s)")
    plt.ylabel("Numero pacchetti")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig("./reports/packets_over_time.png")
    plt.show()

    print("[INFO] Grafici salvati in ./reports/")

if __name__ == "__main__":
    main()

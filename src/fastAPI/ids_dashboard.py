import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="LogAIzer", layout="wide")
st.title("🛡 IDS Demo Dashboard")

# 📘 Legenda
st.sidebar.header("Legenda attacchi (8 feature top-K)")
st.sidebar.markdown("""
| Caso            | Src Bytes | Dst Bytes | same_srv_rate | dst_host_srv_count | dst_host_same_srv_rate | Flag | logged_in | diff_srv_rate | Risultato previsto |
|-----------------|-----------|-----------|---------------|--------------------|------------------------|------|-----------|---------------|--------------------|
| **Normale**     | 234       | 397       | 1             | 255                | 1                      | SF   | 1         | 0             | normal             |
| **TCP Flood**   | 0         | 0         | 0             | 11                 | 0                      | S0   | 0         | 0             | attack             |
| **Brute Force** | 32        | 93        | 1             | 183                | 0                      | SF   | 1         | 0             | attack             |
| **Probe**       | 8         | 0         | 1             | 66                 | 1                      | SF   | 0         | 0             | attack             |
""")

# === Form input ===
st.header("Invia un pacchetto simulato")
with st.form("predict_form"):
    ip = st.text_input("IP", "192.168.1.10")
    protocol = st.selectbox("Protocol", ["tcp", "udp", "icmp"])
    service = st.text_input("Service", "http")
    flag = st.text_input("Flag", "SF")

    src_bytes = st.number_input("Src Bytes", value=100)
    dst_bytes = st.number_input("Dst Bytes", value=200)
    same_srv_rate = st.number_input("same_srv_rate", value=1.0)
    dst_host_srv_count = st.number_input("dst_host_srv_count", value=255)
    dst_host_same_srv_rate = st.number_input("dst_host_same_srv_rate", value=1.0)
    logged_in = st.number_input("logged_in", value=1)
    diff_srv_rate = st.number_input("diff_srv_rate", value=0.0)

    submit = st.form_submit_button("Invia pacchetto")

if submit:
    resp = requests.post(f"{API_URL}/predict", json={
        "ip": ip,
        "protocol": protocol,
        "service": service,
        "flag": flag,
        "src_bytes": src_bytes,
        "dst_bytes": dst_bytes,
        "same_srv_rate": same_srv_rate,
        "dst_host_srv_count": dst_host_srv_count,
        "dst_host_same_srv_rate": dst_host_same_srv_rate,
        "logged_in": logged_in,
        "diff_srv_rate": diff_srv_rate
    })
    st.success(resp.json())

# === Logs ===
st.header("Log eventi")
try:
    logs = requests.get(f"{API_URL}/logs").json()
    if logs:
        df = pd.DataFrame(logs)
        st.dataframe(df)

        st.subheader("Statistiche attacchi")
        stats = df["prediction"].value_counts()
        st.bar_chart(stats)
except Exception as e:
    st.error(f"Errore nel recupero log: {e}")

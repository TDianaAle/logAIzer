import streamlit as st
import requests
import pandas as pd

API_URL = "http://localhost:8000"

st.set_page_config(page_title="IDS Demo", layout="wide")
st.title("🛡 IDS Demo Dashboard")

# 📘 Legenda valori
st.sidebar.header("Legenda attacchi")
st.sidebar.markdown("""
| Caso | Protocol | Service | Flag | Src Bytes | Dst Bytes | Risultato previsto |
|------|----------|---------|------|-----------|-----------|---------------------|
| **Normale** | tcp | http | ACK | 100 | 200 | normal |
| **SYN flood** | tcp | http | SYN | 0 | 0 | attack (SYN flood) |
| **Brute force** | tcp | ftp | ACK | 1500 | 100 | attack (brute force) |
| **Network probe** | udp | dns | OTH | 50 | 0 | attack (probe) |
| **Ping sweep** | icmp | other | OTH | 10 | 0 | attack (ping sweep) |
""")

# Form input
st.header("Invia un pacchetto simulato")
with st.form("predict_form"):
    ip = st.text_input("IP", "192.168.1.10")
    protocol = st.selectbox("Protocol", ["tcp", "udp", "icmp"])
    service = st.text_input("Service", "http")
    flag = st.text_input("Flag", "ACK")
    src_bytes = st.number_input("Src Bytes", value=100)
    dst_bytes = st.number_input("Dst Bytes", value=200)
    submit = st.form_submit_button("Invia pacchetto")

if submit:
    resp = requests.post(f"{API_URL}/predict", json={
        "ip": ip,
        "protocol": protocol,
        "service": service,
        "flag": flag,
        "src_bytes": src_bytes,
        "dst_bytes": dst_bytes
    })
    st.success(resp.json())

# Logs
st.header("Log eventi")
logs = requests.get(f"{API_URL}/logs").json()
if logs:
    df = pd.DataFrame(logs)
    st.dataframe(df)

    st.subheader("Statistiche attacchi")
    stats = df["prediction"].value_counts()
    st.bar_chart(stats)

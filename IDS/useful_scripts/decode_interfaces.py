from scapy.all import get_if_list, get_if_addr

for iface in get_if_list():
    try:
        ip = get_if_addr(iface)
    except Exception:
        ip = "N/A"
    print(f"{iface} -> {ip}")
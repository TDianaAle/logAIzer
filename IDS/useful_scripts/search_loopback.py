from scapy.all import get_if_list

interfaces = get_if_list()
for i, iface in enumerate(interfaces):
    print(i, iface)
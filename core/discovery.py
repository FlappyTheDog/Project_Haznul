import threading
from scapy.all import ARP, sniff
from core.crypto import secure_hash_mac
from core.database import log_device_packet, init_db
from core.ports import scan_device_ports
import socket

def resolve_hostname(ip):
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except Exception: return "Unknown Device"

def process_sniffed_packet(pkt):
    if not pkt.haslayer(ARP): return
    
    raw_mac = str(pkt.hwsrc).strip().lower()
    ip_addr = str(pkt.psrc).strip()
    
    privacy_id = secure_hash_mac(raw_mac)
    real_host = resolve_hostname(ip_addr)
    active_ports = scan_device_ports(ip_addr)
    
    dev_type = "plug"
    if "tv" in real_host.lower(): dev_type = "tv"
    elif "phone" in real_host.lower() or "iphone" in real_host.lower(): dev_type = "phone"
    elif "mac" in real_host.lower(): dev_type = "computer"

    # Save details out using our split database module
    log_device_packet(privacy_id, ip_addr, real_host, dev_type, active_ports)

def start_background_sniffer_thread():
    init_db()
    sniff_thread = threading.Thread(
        target=lambda: sniff(filter="arp", prn=process_sniffed_packet, store=0),
        daemon=True
    )
    sniff_thread.start()
    print("🚨 BACKGROUND GUARD ACTIVE: Continuous tactical sniffer running...")

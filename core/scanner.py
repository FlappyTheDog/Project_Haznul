import socket
import subprocess
import re
from concurrent.futures import ThreadPoolExecutor
from core.crypto import encrypt_mac
from core.vendor import resolve_vendor

PORTS_TO_SCAN = [80, 443, 22, 8001]

def get_local_ip_range() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
    except Exception:
        ip = "127.0.0.1"
    finally:
        s.close()
    if ip == "127.0.0.1": return "127.0.0.1"
    return ".".join(ip.split(".")[:3]) + "."

def check_port(ip: str, port: int) -> bool:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(0.1)
    try:
        s.connect((ip, port))
        return True
    except Exception: return False
    finally: s.close()

def scan_single_ip(ip: str) -> dict or None:
    arp_res = subprocess.run(["arp", ip], capture_output=True, text=True)
    mac_match = re.search(r"(([0-9a-fA-F]{1,2}:){5}[0-9a-fA-F]{1,2})", arp_res.stdout)
    
    if not mac_match: return None
        
    raw_mac = mac_match.group(0).upper()
    enc_mac = encrypt_mac(raw_mac)
    if not enc_mac: return None

    # Resolve REAL vendor name using the original plaintext mac right now
    vendor_name = resolve_vendor(raw_mac)

    try: name = socket.gethostbyaddr(ip)[0]
    except Exception: name = "Unknown Device"

    open_ports = [p for p in PORTS_TO_SCAN if check_port(ip, p)]

    return {
        "ip": ip,
        "name": name,
        "vendor": vendor_name,  # Added true vendor data
        "mac_encrypted": enc_mac,
        "ports": open_ports,
        "status": "Online"
    }

def run_network_scan() -> list:
    base_ip = get_local_ip_range()
    if base_ip == "127.0.0.1": return []

    ips_to_scan = [f"{base_ip}{i}" for i in range(100, 241)]
    ips_to_scan.extend([f"{base_ip}1", f"{base_ip}159"])
    ips_to_scan = list(set(ips_to_scan))

    subprocess.run(["ping", "-c", "2", "-b", f"{base_ip}255"], capture_output=True)

    found_devices = []
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = executor.map(scan_single_ip, ips_to_scan)
        for res in results:
            if res: found_devices.append(res)

    return found_devices

import os
import sqlite3
import socket
from scapy.all import ARP, Ether, srp
from core.crypto import secure_hash_mac

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, "data", "home_safety.db")

# Target ports to actively probe on each device
PORTS_TO_CHECK = [22, 80, 443, 8001]

def init_db():
    os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            privacy_id TEXT PRIMARY KEY, ip TEXT, host TEXT, custom TEXT, 
            dev_type TEXT, trusted INTEGER, is_muted INTEGER,
            spoof INTEGER, open_ports TEXT, is_blocked INTEGER, 
            baseline INTEGER, current INTEGER, first_seen TEXT
        )
    """)
    conn.commit()
    conn.close()

def resolve_hostname(ip):
    try:
        hostname, _, _ = socket.gethostbyaddr(ip)
        return hostname
    except Exception: 
        return "Unknown Device"

def scan_device_ports(ip: str) -> str:
    """Actively probes target ports to find what is open on the device."""
    open_ports = []
    for port in PORTS_TO_CHECK:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.15)  # Fast connection timeout
        try:
            s.connect((ip, port))
            open_ports.append(str(port))
        except Exception:
            pass
        finally:
            s.close()
    return ", ".join(open_ports) if open_ports else "None active"

def run_network_discovery():
    print("📡 Initializing dynamic network airspace scan...")
    init_db()
    
    try:
        ans, _ = srp(Ether(dst="ff:ff:ff:ff:ff:ff")/ARP(pdst="192.168.1.0/24"), timeout=3, verbose=False)
        
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        discovered_count = 0
        
        for snd, rcv in ans:
            raw_mac = str(rcv.hwsrc).strip().lower()
            ip_addr = str(rcv.psrc).strip()
            
            privacy_id = secure_hash_mac(raw_mac)
            real_host = resolve_hostname(ip_addr)
            
            # Run the active port scan check right now
            active_ports = scan_device_ports(ip_addr)
            
            exists = cursor.execute("SELECT privacy_id FROM devices WHERE privacy_id = ?", (privacy_id,)).fetchone()
            
            if not exists:
                dev_type = "plug"
                if "tv" in real_host.lower(): dev_type = "tv"
                elif "phone" in real_host.lower() or "iphone" in real_host.lower(): dev_type = "phone"
                elif "mac" in real_host.lower() or "computer" in real_host.lower(): dev_type = "computer"
                elif "router" in real_host.lower() or "gateway" in real_host.lower(): dev_type = "router"

                cursor.execute("""
                    INSERT INTO devices (privacy_id, ip, host, custom, dev_type, trusted, is_muted, open_ports)
                    VALUES (?, ?, ?, 'None', ?, 0, 0, ?)
                """, (privacy_id, ip_addr, real_host, dev_type, active_ports))
                discovered_count += 1
            else:
                cursor.execute("UPDATE devices SET ip = ?, host = ?, open_ports = ? WHERE privacy_id = ?", (ip_addr, real_host, active_ports, privacy_id))
                
        conn.commit()
        conn.close()
        print(f"🎯 Scan complete! Found/updated {discovered_count} unique nodes inside data/home_safety.db.")
    except Exception as e:
        print(f"❌ Scan interrupted: {e}")

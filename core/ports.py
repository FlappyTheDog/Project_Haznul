import socket

PORTS_TO_CHECK = [22, 80, 443, 8001]

def scan_device_ports(ip: str) -> str:
    open_ports = []
    for port in PORTS_TO_CHECK:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.12)
        try:
            s.connect((ip, port))
            open_ports.append(str(port))
        except Exception: pass
        finally: s.close()
    return ", ".join(open_ports) if open_ports else "None active"

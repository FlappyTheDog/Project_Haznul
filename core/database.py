import os
import sqlite3
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_NAME = os.path.join(BASE_DIR, "data", "home_safety.db")
OFFLINE_THRESHOLD_SECONDS = 600  # Mark offline after 10 minutes of silence

def init_db():
    os.makedirs(os.path.dirname(DB_NAME), exist_ok=True)
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Added last_seen timestamp tracking to the SQL schema definition
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS devices (
            privacy_id TEXT PRIMARY KEY, ip TEXT, host TEXT, custom TEXT, 
            dev_type TEXT, trusted INTEGER, is_muted INTEGER, 
            open_ports TEXT, last_seen REAL
        )
    """)
    conn.commit()
    conn.close()

def log_device_packet(privacy_id: str, ip: str, host: str, dev_type: str, ports: str):
    """Saves or updates a device record, shifting its timestamp to the current millisecond."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    current_time = time.time()
    
    exists = cursor.execute("SELECT privacy_id FROM devices WHERE privacy_id = ?", (privacy_id,)).fetchone()
    if not exists:
        cursor.execute("""
            INSERT INTO devices (privacy_id, ip, host, custom, dev_type, trusted, is_muted, open_ports, last_seen)
            VALUES (?, ?, ?, 'None', ?, 0, 0, ?, ?)
        """, (privacy_id, ip, host, dev_type, ports, current_time))
    else:
        cursor.execute("""
            UPDATE devices SET ip = ?, host = ?, open_ports = ?, last_seen = ? 
            WHERE privacy_id = ?
        """, (ip, host, ports, current_time, privacy_id))
    conn.commit()
    conn.close()

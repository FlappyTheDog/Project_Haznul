import os
import hashlib
from dotenv import load_dotenv, set_key

ENV_FILE = ".env"
load_dotenv(ENV_FILE)

if not os.environ.get("MAC_SALT"):
    generated_salt = os.urandom(16).hex()
    set_key(ENV_FILE, "MAC_SALT", generated_salt)
    load_dotenv(ENV_FILE)

SALT = os.environ.get("MAC_SALT", "default_salt_string")

def secure_hash_mac(mac_address: str) -> str:
    """Hashes the MAC address cleanly so it can never be decrypted or exposed."""
    if not mac_address: return ""
    hasher = hashlib.sha256()
    hasher.update((mac_address.strip().lower() + SALT).encode())
    return hasher.hexdigest()

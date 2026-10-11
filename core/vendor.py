import os
import json
import time
import requests

CACHE_FILE = os.path.join("data", "vendor_cache.json")

def load_cache() -> dict:
    if not os.path.exists(CACHE_FILE) or os.path.getsize(CACHE_FILE) == 0: return {}
    with open(CACHE_FILE, "r") as f:
        try: return json.load(f)
        except: return {}

def save_cache(cache_data: dict):
    os.makedirs("data", exist_ok=True)
    with open(CACHE_FILE, "w") as f: json.dump(cache_data, f, indent=4)

def resolve_vendor_online(mac_address: str) -> str:
    """Cross-references the MAC prefix online with rate-limit file cache matching."""
    if not mac_address or mac_address == "00:00:00:00:00:00": return "Unknown Vendor"
    
    parts = mac_address.strip().split(":")
    prefix = ":".join([p.zfill(2).upper() for p in parts])[:8]
    
    cache = load_cache()
    if prefix in cache:
        return cache[prefix]
        
    try:
        time.sleep(1.1)  # API safe timing pacing gap
        url = f"https://macvendors.com{prefix}"
        response = requests.get(url, timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        
        if response.status_code == 200:
            vendor_name = response.text.strip()
        elif response.status_code == 404:
            vendor_name = "Generic/Unregistered"
        else:
            return "Lookup Pending"
            
        cache[prefix] = vendor_name
        save_cache(cache)
        return vendor_name
    except Exception:
        return "Unknown Vendor"

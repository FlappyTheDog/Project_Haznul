import os
import sqlite3
from flask import Blueprint, render_template_string, redirect, url_for, request, session
from web.home import terminal_layout

network_bp = Blueprint('network', __name__)
DB_FILE = "data/home_safety.db"

def load_devices_from_db(filter_unnamed: bool = False) -> list:
    if not os.path.exists(DB_FILE): return []
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    try:
        if filter_unnamed:
            cursor.execute("SELECT privacy_id, ip, host, custom, dev_type, open_ports FROM devices WHERE custom = 'None' OR custom = '' ORDER BY ip ASC")
        else:
            cursor.execute("SELECT privacy_id, ip, host, custom, dev_type, open_ports FROM devices ORDER BY ip ASC")
        return [dict(row) for row in cursor.fetchall()]
    except sqlite3.OperationalError: return []
    finally: conn.close()

@network_bp.route("/network")
def network_panel():
    if not session.get("logged_in"): return redirect(url_for("auth.login"))
    
    filter_active = request.args.get('unnamed', 'false') == 'true'
    devices = load_devices_from_db(filter_unnamed=filter_active)
    
    network_content = f"""
    <div class="terminal-header" style="margin-top: 20px;">AIRSPACE NODE CONTROL INDEX // COUNTER: {len(devices)}</div>
    <div class="controls">
        <div>
            {"<a href='/network' class='filter-link active-filter'>[SHOW ALL NODES]</a>" if filter_active else "<a href='/network?unnamed=true' class='filter-link'>[FILTER UNNAMED ONLY]</a>"}
        </div>
        <form action="/scan" method="POST"><button type="submit">EXECUTE DISCOVERY SCAN</button></form>
    </div>
    <table>
        <thead>
            <tr><th>NODE HOSTNAME</th><th>DEVICE NAME</th><th>IP ADDRESS</th><th>PROFILE TYPE</th><th>OPEN PORTS</th></tr>
        </thead>
        <tbody>
            {"".join([f"<tr><td>{d['host']}</td><td><form action='/update_custom' method='POST' style='display:flex; gap:8px; margin:0;'><input type='hidden' name='privacy_id' value='{d['privacy_id']}'><input type='hidden' name='redirect_unnamed' value='{'true' if filter_active else 'false'}'><input type='text' name='custom_name' value='{'' if d['custom'] == 'None' else d['custom']}' placeholder='Assign name...' class='terminal-input'><button type='submit' class='mini-btn'>SAVE</button></form></td><td>{d['ip']}</td><td><span class='badge'>{d['dev_type']}</span></td><td>{d['open_ports']}</td></tr>" for d in devices])}
            {"<tr><td colspan='5' style='text-align:center; padding:30px;'>NO COMPATIBLE DEVICE NODES INDEXED.</td></tr>" if not devices else ""}
        </tbody>
    </table>
    """
    return render_template_string(terminal_layout(network_content, active_tab="network"))

@network_bp.route("/update_custom", methods=["POST"])
def update_custom():
    if not session.get("logged_in"): return redirect(url_for("auth.login"))
    privacy_id = request.form.get("privacy_id")
    custom_name = request.form.get("custom_name", "").strip() or "None"
    redirect_unnamed = request.form.get("redirect_unnamed", "false") == "true"
    
    if privacy_id:
        conn = sqlite3.connect(DB_FILE)
        cursor = conn.cursor()
        cursor.execute("UPDATE devices SET custom = ? WHERE privacy_id = ?", (custom_name, privacy_id))
        conn.commit()
        conn.close()
        
    return redirect(url_for('network.network_panel', unnamed='true' if redirect_unnamed else 'false'))

@network_bp.route("/scan", methods=["POST"])
def trigger_scan():
    if not session.get("logged_in"): return redirect(url_for("auth.login"))
    from core.discovery import run_network_discovery
    run_network_discovery()
    return redirect(url_for('network.network_panel'))

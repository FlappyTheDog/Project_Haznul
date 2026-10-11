import os
from flask import Flask, send_from_directory
from web.auth import auth_bp
from web.home import home_bp
from web.network import network_bp
from core.discovery import start_background_sniffer_thread  # <-- Add this import

app = Flask(__name__)
app.secret_key = "wety_terminal_secure_cookie_override"

app.register_blueprint(auth_bp)
app.register_blueprint(home_bp)
app.register_blueprint(network_bp)

@app.route('/static/theme1.css')
def serve_theme_fallback():
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'web', 'static')
    return send_from_directory(static_dir, 'theme1.css')

if __name__ == "__main__":
    # Boot the 24/7 background airspace sniffing engine instantly
    start_background_sniffer_thread()  # <-- Add this function execution call
    app.run(host="0.0.0.0", port=8001, debug=True, use_reloader=False) # use_reloader=False avoids double threads

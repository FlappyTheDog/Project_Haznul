from flask import Blueprint, render_template_string, redirect, url_for, request, session

auth_bp = Blueprint('auth', __name__)
ADMIN_PASSWORD = "password123"

@auth_bp.route("/")
@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("logged_in"):
        return redirect(url_for("home.home_landing"))
        
    error_msg = ""
    if request.method == "POST":
        if request.form.get("password") == ADMIN_PASSWORD:
            session["logged_in"] = True
            return redirect(url_for("home.home_landing"))
        error_msg = "ACCESS DENIED: INVALID SECURITY KEY CODE"

    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="/static/theme1.css">
        <title>LOGIN - SECURE SECURITY GATEWAY</title>
    </head>
    <body style="display: flex; justify-content: center; align-items: center; height: 100vh; padding: 0;">
        <div class="container" style="width: 400px; text-align: center;">
            <div class="terminal-header">SECURITY ACCESS REQUIRED</div>
            <p style="font-size: 13px; color: rgba(34,255,102,0.7); margin-bottom: 20px;">ENTER CRITICAL CORE PASSKEY TERMINAL CODE</p>
            {% if error %}
                <div style="color: #ff3b30; font-weight: bold; margin-bottom: 15px; font-size: 13px;">{{ error }}</div>
            {% endif %}
            <form method="POST" action="/login">
                <input type="password" name="password" placeholder="ENTER ACCESS CODE..." class="terminal-input" style="width: 80%; padding: 10px; text-align: center; margin-bottom: 20px;" autofocus autocomplete="off"><br>
                <button type="submit" style="width: 90%;">INITIATE DECRYPTION</button>
            </form>
        </div>
    </body>
    </html>
    """, error=error_msg)

@auth_bp.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("auth.login"))

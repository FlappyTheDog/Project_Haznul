from flask import Blueprint, render_template_string, redirect, url_for, session

home_bp = Blueprint('home', __name__)

def terminal_layout(content_html: str, active_tab: str) -> str:
    """Shared layout wrapper serving the navigation navbar."""
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <link rel="stylesheet" href="/static/theme1.css">
        <title>INTERNAL TERMINAL - WEYLAND-YUTANI HUBS</title>
    </head>
    <body>
        <div class="container">
            <div class="terminal-navbar">
                <a href="/home" class="nav-btn {'active-nav' if active_tab == 'home' else ''}">[ 01 // HOME_PAGE ]</a>
                <a href="/network" class="nav-btn {'active-nav' if active_tab == 'network' else ''}">[ 02 // NETWORK_AIRSPACE ]</a>
                <a href="/logout" class="nav-btn" style="margin-left: auto; color: #ff3b30;">[ SHUTDOWN_SESSION ]</a>
            </div>
            {content_html}
        </div>
    </body>
    </html>
    """

@home_bp.route("/home")
def home_landing():
    if not session.get("logged_in"): return redirect(url_for("auth.login"))
    
    content = """
    <div class="terminal-header" style="margin-top: 20px;">CORE CONSOLE HOME DIRECTORY</div>
    <div style="line-height: 1.6; margin: 30px 0;">
        <p>>>> ACCESS LEVEL: ADMINISTRATIVE ROOT OVERRIDE</p>
        <p>>>> Welcome to your tactical airspace command console interface terminal module.</p>
        <p>>>> This hub allows you to audit all active hardware devices broadcasting data over-the-air in your local residency airspace.</p>
        <p>>>> Tap the navigation menu bars above to query live node channels or adjust network filters.</p>
    </div>
    <div class="footer-nav">SYSTEM VERSION: 2.4.1-MAC // PLATFORM DISK HEALTH: STABLE</div>
    """
    return render_template_string(terminal_layout(content, active_tab="home"))

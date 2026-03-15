"""
Web Dashboard — Real-time bot monitoring via HTTP.

Game-agnostic: displays logs and stats from any game bot.
Each game provides its own stat keys and values.
"""
import os
import time
from datetime import datetime
from string import Template
from threading import Thread
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Global state shared between bot and dashboard
_logs = []
_stats = {}
_paused = False
_start_time = time.time()
MAX_LOGS = 200


def is_paused() -> bool:
    return _paused


class BotLogger:
    """Logger that writes to console, file, and feeds the web dashboard."""

    def __init__(self, log_dir: str = "logs", log_file: str = "bot.log"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
        self.log_path = os.path.join(log_dir, log_file)
        self.start_time = time.time()

    def log(self, message: str):
        timestamp = datetime.now().strftime("%H:%M:%S")
        entry = f"[{timestamp}] {message}"
        print(entry)

        _logs.append(entry)
        if len(_logs) > MAX_LOGS:
            _logs.pop(0)

        daily_path = os.path.join(
            self.log_dir,
            f"bot-{datetime.now().strftime('%Y-%m-%d')}.log",
        )
        with open(daily_path, "a") as f:
            f.write(entry + "\n")
        with open(self.log_path, "a") as f:
            f.write(entry + "\n")

    def update_stats(self, stats: dict):
        global _stats
        _stats = stats


# Default HTML template — games can override with their own
_HTML = Template("""<!DOCTYPE html>
<html>
<head>
<title>4X Game Agent</title>
<meta http-equiv="refresh" content="10">
<style>
body { font-family: monospace; background: #0d1117; color: #c9d1d9;
       padding: 20px; max-width: 900px; margin: 0 auto; }
h1 { color: #58a6ff; font-size: 20px; }
.stats { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
.stat-box { background: #161b22; border: 1px solid #30363d;
            border-radius: 8px; padding: 12px; min-width: 100px; flex: 1; }
.stat-value { font-size: 22px; font-weight: bold; color: #3fb950; }
.stat-label { font-size: 11px; color: #8b949e; margin-top: 4px; }
.log-box { background: #161b22; border: 1px solid #30363d;
           border-radius: 8px; padding: 15px; max-height: 600px;
           overflow-y: auto; }
.log-line { margin: 2px 0; font-size: 12px; border-bottom: 1px solid #21262d;
            padding: 3px 0; white-space: pre-wrap; }
.log-line.error { color: #f85149; }
.log-line.success { color: #3fb950; }
.log-line.action { color: #79c0ff; }
.pause-btn { padding: 10px 28px; font-size: 14px; font-weight: bold;
             border: none; border-radius: 8px; cursor: pointer;
             margin-bottom: 16px; }
.pause-btn.running { background: #da3633; color: white; }
.pause-btn.paused { background: #3fb950; color: white; }
</style>
</head>
<body>
<h1>$title</h1>
<p style="color:#8b949e; font-size:12px;">Auto-refresh 10s | $uptime</p>
<a href="/toggle"><button class="pause-btn $btn_class">$btn_text</button></a>
<div class="stats">$stat_boxes</div>
<div class="log-box">$log_lines</div>
</body>
</html>""")


class _DashboardHandler(BaseHTTPRequestHandler):
    game_title = "4X Game Agent"

    def log_message(self, *args):
        pass

    def do_GET(self):
        global _paused
        if urlparse(self.path).path == "/toggle":
            _paused = not _paused
            _logs.append(
                f"[{datetime.now().strftime('%H:%M:%S')}] "
                f"{'PAUSED' if _paused else 'RESUMED'} by user"
            )
            self.send_response(302)
            self.send_header("Location", "/")
            self.end_headers()
            return

        uptime_secs = int(time.time() - _start_time)
        h, m, s = uptime_secs // 3600, (uptime_secs % 3600) // 60, uptime_secs % 60

        # Build stat boxes from whatever stats the game provides
        stat_html = ""
        for key, val in _stats.items():
            if isinstance(val, (dict, list)):
                continue
            label = key.replace("_", " ").title()
            stat_html += (
                f'<div class="stat-box">'
                f'<div class="stat-value">{val}</div>'
                f'<div class="stat-label">{label}</div></div>\n'
            )

        log_html = ""
        for line in reversed(_logs[-100:]):
            css = "log-line"
            if "ERROR" in line:
                css += " error"
            elif any(w in line for w in ("OK", "SUCCESS", "reward", "claim")):
                css += " success"
            elif any(w in line for w in ("TAP", "PAUSED", "RESUMED")):
                css += " action"
            log_html += f'<div class="{css}">{line}</div>\n'

        html = _HTML.substitute(
            title=self.game_title,
            uptime=f"{h:02d}:{m:02d}:{s:02d}",
            stat_boxes=stat_html,
            log_lines=log_html,
            btn_class="paused" if _paused else "running",
            btn_text="RESUME" if _paused else "PAUSE",
        )

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(html.encode())


def start_dashboard(port: int = 8080, title: str = "4X Game Agent"):
    """Start the web dashboard in a background thread."""
    _DashboardHandler.game_title = title
    server = HTTPServer(("0.0.0.0", port), _DashboardHandler)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    print(f"Dashboard: http://localhost:{port}")
    return server

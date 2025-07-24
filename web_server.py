from flask import Flask, jsonify
import threading
import os
from datetime import datetime

app = Flask(__name__)

# Base status info
def get_bot_status():
    return {
        "status": "online",
        "bot": "Pakistan RP Community Bot",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "platform": "Glitch",
        "uptime_strategy": "Staggered Multi-Monitor"
    }

# Endpoint 1: Main status page (HTML)
@app.route('/')
def home():
    return '''
    <h1>🇵🇰 Pakistan RP Community Bot</h1>
    <p>Status: <span style="color: green;">✅ Online and Running</span></p>
    <p>Platform: <span style="color: blue;">Koyeb Hosting</span></p>
    <p>Uptime Strategy: <span style="color: purple;">Staggered Multi-Monitor</span></p>
    <hr>
    <p>Bot Features:</p>
    <ul>
        <li>🎫 Advanced Ticket System</li>
        <li>📋 Smart Rule Database</li>
        <li>📢 Announcement System</li>
        <li>👥 Member Management</li>
        <li>⚡ Automation Engine</li>
    </ul>
    <p><small>Last ping: ''' + datetime.now().strftime("%H:%M:%S") + '''</small></p>
    '''

# Endpoint 2: JSON status
@app.route('/status')
def status():
    return jsonify(get_bot_status())

# Endpoint 3: Health check
@app.route('/health')
def health():
    return jsonify({
        "health": "ok", 
        "message": "Bot is running smoothly",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "monitor": "health-check"
    })

# Endpoint 4: Simple ping
@app.route('/ping')
def ping():
    return jsonify({
        "ping": "pong",
        "server": "active", 
        "time": datetime.now().strftime("%H:%M:%S"),
        "monitor": "ping-check"
    })

# Endpoint 5: Keep-alive endpoint
@app.route('/keepalive')
def keepalive():
    return jsonify({
        "alive": True,
        "service": "Pakistan RP Bot",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "monitor": "keepalive-check"
    })

# Endpoint 6: Uptime info
@app.route('/uptime')
def uptime():
    return jsonify({
        "uptime": "active",
        "monitors": 5,
        "strategy": "staggered-pings",
        "interval": "60-seconds",
        "timestamp": datetime.now().strftime("%H:%M:%S")
    })

def run():
    port = int(os.environ.get('PORT', 8000))  #koyeb uses port 8000
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()
    print("🌐 Multi-endpoint web server started")
    print("📡 Ready for staggered monitoring strategy")

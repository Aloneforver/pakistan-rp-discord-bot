from flask import Flask
import threading
import os

app = Flask(__name__)

@app.route('/')
def home():
    return '''
    <h1>🇵🇰 Pakistan RP Community Bot</h1>
    <p>Status: <span style="color: green;">✅ Online and Running</span></p>
    <p>This endpoint keeps the bot alive on Render.</p>
    <hr>
    <p>Bot Features:</p>
    <ul>
        <li>🎫 Advanced Ticket System</li>
        <li>📋 Smart Rule Database</li>
        <li>📢 Announcement System</li>
        <li>👥 Member Management</li>
        <li>⚡ Automation Engine</li>
    </ul>
    '''

@app.route('/status')
def status():
    return {"status": "online", "bot": "Pakistan RP Community Bot"}

@app.route('/health')
def health():
    return {"health": "ok", "message": "Bot is running smoothly"}

def run():
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = threading.Thread(target=run)
    t.daemon = True
    t.start()
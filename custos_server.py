#!/usr/bin/env python3
"""
Custos Server - Secure network token management service
"""

import os
import sys
import json
import hashlib
import secrets
import logging
from datetime import datetime
from pathlib import Path
from flask import Flask, request, jsonify, render_template_string
from functools import wraps

app = Flask(__name__)

# Configuration paths
BASE_DIR = Path("/opt/custos")
DATA_DIR = BASE_DIR / "data"
CONFIG_FILE = BASE_DIR / "config.json"
TOKEN_FILE = DATA_DIR / "tokens.json"
STATE_FILE = DATA_DIR / "state.json"
LOG_FILE = DATA_DIR / "access.log"

# Ensure directories exist
BASE_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)


class CustosServer:
    """Manages secure tokens and access control"""
    
    def __init__(self):
        self.config = self._load_config()
        self.tokens = self._load_tokens()
        self.locked = self._load_state().get('locked', False)
        
    def _load_config(self):
        """Load configuration from disk"""
        if not CONFIG_FILE.exists():
            raise FileNotFoundError("Config file not found. Run setup first.")
        
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    
    def _load_tokens(self):
        """Load secure tokens from disk"""
        if TOKEN_FILE.exists():
            with open(TOKEN_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def _load_state(self):
        """Load server state from disk"""
        if STATE_FILE.exists():
            with open(STATE_FILE, 'r') as f:
                return json.load(f)
        return {}
    
    def save_tokens(self):
        """Persist tokens to disk with proper permissions"""
        with open(TOKEN_FILE, 'w') as f:
            json.dump(self.tokens, f, indent=2)
        os.chmod(TOKEN_FILE, 0o600)
    
    def save_state(self):
        """Persist server state to disk with proper permissions"""
        state = {
            'locked': self.locked,
            'last_updated': datetime.now().isoformat()
        }
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
        os.chmod(STATE_FILE, 0o600)
    
    def verify_token(self, token):
        """Verify API token against stored hashes"""
        if not token:
            return None
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        for name, stored_hash in self.config['tokens'].items():
            if secrets.compare_digest(stored_hash, token_hash):
                return name
        return None
    
    def destroy_all_tokens(self):
        """Securely destroy all stored tokens"""
        # Clear from memory
        self.tokens = {}
        
        # Overwrite file with random data
        if TOKEN_FILE.exists():
            with open(TOKEN_FILE, 'wb') as f:
                f.write(os.urandom(4096))
            TOKEN_FILE.unlink()
        
        # Save empty state
        self.save_tokens()


# Initialize server (will fail if not configured)
try:
    server = CustosServer()
except FileNotFoundError:
    logging.error("Server not configured. Run setup-custos.py first.")
    exit(1)


def require_auth(allowed_roles):
    """Authentication decorator"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            # Check header first, then form data
            auth = request.headers.get('Authorization', '')
            if auth.startswith('Bearer '):
                token = auth[7:]
            else:
                token = request.form.get('token', '')
                
            role = server.verify_token(token)
            if not role or role not in allowed_roles:
                return jsonify({"error": "Unauthorized"}), 401
                
            return f(*args, role=role, **kwargs)
        return wrapped
    return decorator


@app.route('/')
def control_panel():
    """Mobile-friendly control panel"""
    return render_template_string('''
<!DOCTYPE html>
<html>
<head>
    <title>Vigil Control</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <style>
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            margin: 0;
            padding: 20px;
            background: #1a1a1a;
            color: white;
        }
        .container {
            max-width: 400px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            margin-bottom: 30px;
        }
        .status {
            background: #2a2a2a;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
            text-align: center;
            border: 2px solid;
        }
        .status.locked {
            border-color: #ff6b6b;
            background: #2a1515;
        }
        .status.unlocked {
            border-color: #51cf66;
            background: #152a15;
        }
        .status h2 {
            margin: 0 0 10px 0;
            font-size: 24px;
        }
        .status p {
            margin: 0;
            opacity: 0.7;
            font-size: 14px;
        }
        .controls {
            background: #2a2a2a;
            padding: 25px;
            border-radius: 15px;
            margin-bottom: 25px;
        }
        input {
            width: 100%;
            padding: 15px;
            margin-bottom: 15px;
            border: 2px solid #3a3a3a;
            border-radius: 10px;
            background: #1a1a1a;
            color: white;
            font-size: 16px;
            box-sizing: border-box;
        }
        input:focus {
            outline: none;
            border-color: #4a9eff;
        }
        button {
            width: 100%;
            padding: 18px;
            margin: 8px 0;
            border: none;
            border-radius: 10px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        button:active {
            transform: scale(0.98);
        }
        .lock-btn {
            background: #ff9f43;
            color: white;
        }
        .unlock-btn {
            background: #10ac84;
            color: white;
        }
        .wipe-section {
            background: #2a1515;
            padding: 25px;
            border-radius: 15px;
            border: 2px solid #ff6b6b;
            margin-top: 40px;
        }
        .wipe-btn {
            background: #ee5a6f;
            color: white;
        }
        .wipe-warning {
            text-align: center;
            margin-bottom: 15px;
            opacity: 0.8;
            font-size: 14px;
        }
        #message {
            padding: 15px;
            border-radius: 10px;
            margin-bottom: 20px;
            text-align: center;
            display: none;
        }
        .success {
            background: #10ac84;
            color: white;
        }
        .error {
            background: #ee5a6f;
            color: white;
        }
        .loading {
            opacity: 0.6;
            pointer-events: none;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔐 Custos Control</h1>
        
        <div class="status {{ 'locked' if locked else 'unlocked' }}">
            <h2>{{ 'LOCKED 🔒' if locked else 'UNLOCKED 🔓' }}</h2>
            <p>{{ time }}</p>
        </div>
        
        <div id="message"></div>
        
        <div class="controls">
            <input type="password" 
                   id="token" 
                   placeholder="Enter emergency token" 
                   autocomplete="off"
                   autocorrect="off"
                   autocapitalize="off"
                   spellcheck="false" />
            
            {% if not locked %}
            <button class="lock-btn" onclick="lockServer()">
                🔒 Lock Server
            </button>
            {% else %}
            <button class="unlock-btn" onclick="unlockServer()">
                🔓 Unlock Server
            </button>
            {% endif %}
        </div>
        
        <div class="wipe-section">
            <div class="wipe-warning">
                ⚠️ This will permanently destroy all stored data
            </div>
            <button class="wipe-btn" onclick="confirmWipe()">
                🔥 Emergency Reset
            </button>
        </div>
    </div>
    
    <script>
        let isLoading = false;
        
        function setLoading(loading) {
            isLoading = loading;
            document.body.classList.toggle('loading', loading);
        }
        
        function showMessage(text, isError) {
            const msg = document.getElementById('message');
            msg.textContent = text;
            msg.className = isError ? 'error' : 'success';
            msg.style.display = 'block';
            
            setTimeout(() => {
                msg.style.display = 'none';
            }, 3000);
        }
        
        async function apiCall(endpoint, method = 'POST', body = null) {
            if (isLoading) return;
            
            const token = document.getElementById('token').value.trim();
            if (!token) {
                showMessage('Please enter token', true);
                return;
            }
            
            setLoading(true);
            
            try {
                const options = {
                    method: method,
                    headers: {
                        'Authorization': 'Bearer ' + token,
                        'Content-Type': 'application/json'
                    }
                };
                
                if (body) {
                    options.body = JSON.stringify(body);
                }
                
                const resp = await fetch(endpoint, options);
                
                if (resp.ok) {
                    showMessage('Success!', false);
                    setTimeout(() => location.reload(), 1000);
                } else {
                    const error = await resp.json();
                    showMessage(error.error || 'Request failed', true);
                }
            } catch (e) {
                showMessage('Network error', true);
            } finally {
                setLoading(false);
            }
        }
        
        function lockServer() {
            apiCall('/lock');
        }
        
        function unlockServer() {
            apiCall('/unlock');
        }
        
        function confirmWipe() {
            const msg = 'WARNING: This will PERMANENTLY destroy all stored data.\\n\\n' +
                       'This action cannot be undone.\\n\\n' +
                       'Are you absolutely sure?';
                       
            if (confirm(msg)) {
                if (confirm('This is your FINAL warning. Proceed with reset?')) {
                    wipeServer();
                }
            }
        }
        
        async function wipeServer() {
            await apiCall('/wipe', 'DELETE', {confirm: 'DESTROY_ALL_KEYS'});
        }
        
        // Auto-focus token field
        document.getElementById('token').focus();
    </script>
</body>
</html>
    ''', 
        locked=server.locked,
        time=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "locked": server.locked,
        "time": datetime.now().isoformat(),
        "data_count": len(server.tokens)
    })


@app.route('/data/<data_id>', methods=['GET'])
@require_auth(['primary'])
def get_data(data_id, role=None):
    """Retrieve stored data"""
    if server.locked:
        logging.warning(f"Data request while locked: {data_id} by {role}")
        return jsonify({"error": "Service is locked"}), 423
    
    if data_id in server.tokens:
        logging.info(f"Data retrieved: {data_id} by {role}")
        return jsonify({"data": server.tokens[data_id]}), 200
    
    return jsonify({"error": "Data not found"}), 404


@app.route('/data/<data_id>', methods=['PUT'])
@require_auth(['primary', 'setup'])
def store_data(data_id, role=None):
    """Store secure data"""
    data = request.get_json()
    if not data or 'data' not in data:
        return jsonify({"error": "No data provided"}), 400
    
    server.tokens[data_id] = data['data']
    server.save_tokens()
    
    logging.info(f"Data stored: {data_id} by {role}")
    return jsonify({"status": "stored"}), 201


@app.route('/lock', methods=['POST'])
@require_auth(['primary', 'emergency'])
def lock_server(role=None):
    """Lock the server - prevent key access"""
    server.locked = True
    server.save_state()
    logging.warning(f"SERVER LOCKED by {role}")
    
    # Optional: Notify Vigil Pi to unmount drives
    # This would require Vigil Pi to run a listener service
    
    return jsonify({
        "status": "locked",
        "note": "New data requests will be denied."
    }), 200


@app.route('/unlock', methods=['POST'])
@require_auth(['primary', 'emergency'])
def unlock_server(role=None):
    """Unlock the server - allow key access"""
    server.locked = False
    server.save_state()
    logging.info(f"Server unlocked by {role}")
    
    return jsonify({
        "status": "unlocked",
        "note": "Data requests are now allowed."
    }), 200


@app.route('/status/<device_id>', methods=['GET'])
@require_auth(['primary'])
def device_status(device_id, role=None):
    """Check if a device should remain unlocked"""
    # This endpoint could be polled by Vigil Pi to check if it should unmount
    return jsonify({
        "device_id": device_id,
        "locked": server.locked,
        "action": "unmount" if server.locked else "keep_mounted"
    })


@app.route('/wipe', methods=['DELETE'])
@require_auth(['emergency'])
def emergency_wipe(role=None):
    """Emergency wipe - destroy all data"""
    data = request.get_json()
    if not data or data.get('confirm') != 'DESTROY_ALL_KEYS':
        return jsonify({"error": "Confirmation required"}), 400
    
    logging.critical(f"EMERGENCY RESET INITIATED by {role}")
    
    server.destroy_all_tokens()
    
    logging.critical("ALL DATA DESTROYED")
    return jsonify({"status": "All data destroyed"}), 200


if __name__ == '__main__':
    # Production should use gunicorn
    app.run(host='0.0.0.0', port=5555, debug=False)
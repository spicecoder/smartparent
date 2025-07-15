#!/usr/bin/env python3
from flask import Flask, jsonify
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = '/home/pi/smartguard-monitor/data/dns_logs.db'

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    return '''
    <!DOCTYPE html>
    <html>
    <head><title>SmartGuard - Network Monitor</title></head>
    <body>
        <h1>🛡 SmartGuard Network Monitor</h1>
        <p>Real-time DNS monitoring and analysis</p>
        <div id="total-requests">Total Requests: Loading...</div>
        <div id="recent-requests">Recent Requests: Loading...</div>
        <script>
        fetch('/api/stats')
            .then(res => res.json())
            .then(data => {
                document.getElementById('total-requests').textContent = "Total Requests: " + data.total_requests;
            });

        fetch('/api/recent-requests')
            .then(res => res.json())
            .then(data => {
                document.getElementById('recent-requests').textContent = "Recent Requests: " + data.length;
            });
        </script>
    </body>
    </html>
    '''

@app.route('/api/stats')
def api_stats():
    try:
        today = datetime.now().strftime("%Y-%m-%d")
        conn = get_db_connection()
        result = conn.execute(
            "SELECT COUNT(*) FROM dns_logs WHERE substr(timestamp, 1, 10) = ?", (today,)
        ).fetchone()
        conn.close()
        total_requests = result[0] if result else 0
        return jsonify({
            'total_requests': total_requests,
            'status': 'online'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent-requests')
def api_recent_requests():
    try:
        conn = get_db_connection()
        requests = conn.execute(
            "SELECT timestamp, source_ip, queried_domain, record_type, response_code FROM dns_logs ORDER BY id DESC LIMIT 20"
        ).fetchall()
        conn.close()
        return jsonify([dict(row) for row in requests])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

#!/usr/bin/env python3
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import sqlite3
from datetime import datetime

app = Flask(__name__)
CORS(app)

DB_PATH = '../data/smartguard.db'

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return '''
<!DOCTYPE html>
<html>
<head>
    <title>SmartGuard - Network Monitor</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: -apple-system, sans-serif; margin: 0; padding: 20px; background: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                  color: white; padding: 30px; border-radius: 10px; margin-bottom: 20px; }
        .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                     gap: 20px; margin-bottom: 30px; }
        .stat-card { background: white; padding: 20px; border-radius: 8px;
                     box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .stat-value { font-size: 2.5em; font-weight: bold; color: #667eea; }
        .stat-label { color: #666; margin-top: 5px; }
        .requests-table { background: white; border-radius: 8px; overflow: hidden;
                          box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        table { width: 100%; border-collapse: collapse; }
        th { background: #f8f9fa; padding: 15px; text-align: left; font-weight: 600; }
        td { padding: 12px 15px; border-bottom: 1px solid #eee; }
        .status { display: inline-block; width: 10px; height: 10px; border-radius: 50%;
                  margin-right: 8px; }
        .status.online { background: #4caf50; }
        .refresh-btn { background: #667eea; color: white; border: none; padding: 10px 20px;
                      border-radius: 5px; cursor: pointer; margin-bottom: 20px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ SmartGuard Network Monitor</h1>
            <p>Real-time DNS monitoring and analysis</p>
        </div>

        <button class="refresh-btn" onclick="loadData()">🔄 Refresh Data</button>

        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-value" id="total-requests">-</div>
                <div class="stat-label">Total DNS Requests</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="unique-domains">-</div>
                <div class="stat-label">Unique Domains</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="active-devices">-</div>
                <div class="stat-label">Active Devices</div>
            </div>
            <div class="stat-card">
                <div class="stat-value" id="monitoring-status">
                    <span class="status online"></span>Online
                </div>
                <div class="stat-label">System Status</div>
            </div>
        </div>

        <div class="requests-table">
            <h3 style="margin: 0; padding: 20px 20px 0;">Recent DNS Requests</h3>
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Device IP</th>
                        <th>Domain</th>
                        <th>Type</th>
                        <th>Status</th>
                    </tr>
                </thead>
                <tbody id="requests-table">
                    <tr><td colspan="5" style="text-align: center; color: #666;">Loading...</td></tr>
                </tbody>
            </table>
        </div>
    </div>

    <script>
        function loadData() {
            // Load statistics
            fetch('/api/stats')
                .then(response => response.json())
                .then(data => {
                    document.getElementById('total-requests').textContent = data.total_requests || 0;
                    document.getElementById('unique-domains').textContent = data.unique_domains || 0;
                    document.getElementById('active-devices').textContent = data.active_devices || 0;
                })
                .catch(error => console.error('Error loading stats:', error));

            // Load recent requests
            fetch('/api/recent-requests')
                .then(response => response.json())
                .then(data => {
                    const tbody = document.getElementById('requests-table');
                    tbody.innerHTML = '';

                    if (data.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center; color: #666;">No requests yet</td></tr>';
                        return;
                    }

                    data.forEach(request => {
                        const row = tbody.insertRow();
                        row.innerHTML = `
                            <td>${new Date(request.timestamp).toLocaleString()}</td>
                            <td>${request.client_ip}</td>
                            <td>${request.domain}</td>
                            <td>${request.query_type}</td>
                            <td><span class="status online"></span>Logged</td>
                        `;
                    });
                })
                .catch(error => console.error('Error loading requests:', error));
        }

        // Load data on page load
        loadData();

        // Auto-refresh every 10 seconds
        setInterval(loadData, 10000);
    </script>
</body>
</html>
'''

@app.route('/api/stats')
def api_stats():
    """Get system statistics"""
    try:
        conn = get_db_connection()

        total_requests = conn.execute(
            "SELECT COUNT(*) FROM dns_requests WHERE DATE(timestamp) = DATE('now')"
        ).fetchone()[0]

        unique_domains = conn.execute(
            "SELECT COUNT(DISTINCT domain) FROM dns_requests WHERE DATE(timestamp) = DATE('now')"
        ).fetchone()[0]

        active_devices = conn.execute(
            "SELECT COUNT(DISTINCT client_ip) FROM dns_requests WHERE DATE(timestamp) = DATE('now')"
        ).fetchone()[0]

        conn.close()

        return jsonify({
            'total_requests': total_requests,
            'unique_domains': unique_domains,
            'active_devices': active_devices,
            'status': 'online'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/recent-requests')
def api_recent_requests():
    """Get recent DNS requests"""
    try:
        limit = request.args.get('limit', 50)
        conn = get_db_connection()
        requests = conn.execute(
            '''SELECT timestamp, client_ip, domain
               FROM dns_requests
               ORDER BY timestamp DESC
               LIMIT ?''',
            (limit,)
        ).fetchall()
        conn.close()
        return jsonify([dict(row) for row in requests])
    except Exception as e:
        return jsonify({'error': str(e)}), 500



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

from flask import Flask, jsonify, render_template
import sqlite3

app = Flask(__name__)
DB_PATH = 'data/dns_monitor.db'

def query_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute('SELECT id, timestamp, client_ip, query FROM dns_queries ORDER BY timestamp DESC LIMIT 50')
    rows = c.fetchall()
    conn.close()
    return rows

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/queries')
def api_queries():
    rows = query_db()
    data = [{'id': r[0], 'timestamp': r[1], 'client_ip': r[2], 'query': r[3]} for r in rows]
    return jsonify(data)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

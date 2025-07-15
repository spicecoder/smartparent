from flask import Flask, jsonify
import sqlite3
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_FILE = "/home/pi/smartguard-monitor/data/dns_logs.db"

@app.route("/api/logs", methods=["GET"])
def get_logs():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM dns_logs ORDER BY timestamp DESC LIMIT 100")
    rows = cursor.fetchall()
    logs = [dict(row) for row in rows]
    conn.close()
    return jsonify(logs)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

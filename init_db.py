import sqlite3

conn = sqlite3.connect('data/dns_monitor.db')

c = conn.cursor()

# Create tables as per your project requirements
c.execute('''
CREATE TABLE IF NOT EXISTS dns_queries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    client_ip TEXT NOT NULL,
    query TEXT NOT NULL,
    response TEXT,
    ttl INTEGER
)
''')

conn.commit()
conn.close()
print("Database initialized successfully.")

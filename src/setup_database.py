#!/usr/bin/env python3
import sqlite3

def setup_base_database():
    conn = sqlite3.connect('../data/smartguard.db')
    cursor = conn.cursor()

    print("🧱 Creating core database schema...")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dns_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            domain TEXT NOT NULL,
            client_ip TEXT NOT NULL
        )
    ''')
    print("✅ dns_requests table created")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            hostname TEXT,
            ip_address TEXT UNIQUE NOT NULL,
            mac_address TEXT UNIQUE,
            first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ devices table created")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_ip TEXT NOT NULL,
            domain TEXT NOT NULL,
            count INTEGER DEFAULT 1,
            last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ traffic_stats table created")

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_type TEXT NOT NULL,
            message TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ system_events table created")

    # Configuration table if not already present
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuration (
            key TEXT PRIMARY KEY,
            value TEXT,
            description TEXT
        )
    ''')
    print("✅ configuration table ensured")

    conn.commit()
    conn.close()
    print("🎉 Base schema setup complete.")

if __name__ == '__main__':
    setup_base_database()

#!/usr/bin/env python3
import sqlite3
from datetime import datetime

def update_database():
    conn = sqlite3.connect('../data/smartguard.db')
    cursor = conn.cursor()

    print("🔄 Updating database schema...")

    # domain_classifications table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS domain_classifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            domain TEXT UNIQUE NOT NULL,
            category TEXT NOT NULL,
            confidence REAL NOT NULL,
            risk_level TEXT NOT NULL,
            color TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Created domain_classifications table")

    # alert_rules table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alert_rules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            rule_name TEXT NOT NULL,
            category TEXT NOT NULL,
            risk_level TEXT NOT NULL,
            time_threshold INTEGER DEFAULT 300,
            request_threshold INTEGER DEFAULT 10,
            enabled BOOLEAN DEFAULT 1,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Created alert_rules table")

    # alerts table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            alert_type TEXT NOT NULL,
            severity TEXT NOT NULL,
            client_ip TEXT NOT NULL,
            domain TEXT NOT NULL,
            category TEXT NOT NULL,
            message TEXT NOT NULL,
            acknowledged BOOLEAN DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✅ Created alerts table")

    # Insert default rules
    default_rules = [
        ("High Risk Sites", "inappropriate", "high", 60, 1, 1),
        ("Excessive Social Media", "social_media", "medium", 1800, 20, 1),
        ("Late Night Gaming", "gaming", "medium", 300, 5, 1),
        ("Educational Override", "educational", "low", 86400, 100, 0),
    ]

    for rule in default_rules:
        cursor.execute('''
            INSERT OR IGNORE INTO alert_rules 
            (rule_name, category, risk_level, time_threshold, request_threshold, enabled)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', rule)
    print(f"✅ Inserted {len(default_rules)} default alert rules")

    # Configuration override
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuration (
            key TEXT PRIMARY KEY,
            value TEXT,
            description TEXT
        )
    ''')
    cursor.execute('''
        INSERT OR REPLACE INTO configuration (key, value, description)
        VALUES ('classification_enabled', 'true', 'AI classification enabled')
    ''')
    print("✅ Updated configuration")

    conn.commit()
    conn.close()
    print("🎉 Database schema updated successfully!")

def verify_database():
    conn = sqlite3.connect('../data/smartguard.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    required_tables = [
        'dns_requests', 'devices', 'traffic_stats', 'system_events',
        'configuration', 'domain_classifications', 'alert_rules', 'alerts'
    ]

    print("\n📊 Database Schema Verification:")
    for table in required_tables:
        status = "✅" if table in tables else "❌"
        print(f"{status} {table}")

    cursor.execute("SELECT COUNT(*) FROM alert_rules")
    rule_count = cursor.fetchone()[0]
    print(f"\n📋 Alert Rules: {rule_count} configured")

    conn.close()

if __name__ == '__main__':
    update_database()
    verify_database()

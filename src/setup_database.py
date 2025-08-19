#!/usr/bin/env python3
import sqlite3
import os
from datetime import datetime

def create_database():
    """Initialize the SmartGuard monitoring database"""

    # Create data directory if it doesn't exist
    os.makedirs('../data', exist_ok=True)

    # Connect to database
    db_path = '../data/smartguard.db'
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # DNS requests table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dns_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            client_ip TEXT NOT NULL,
            client_mac TEXT,
            domain TEXT NOT NULL,
            query_type TEXT DEFAULT 'A',
            response_ip TEXT,
            response_time_ms INTEGER,
            status TEXT DEFAULT 'logged',
            classification TEXT,
            confidence_score REAL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Device information table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            mac_address TEXT UNIQUE NOT NULL,
            ip_address TEXT,
            hostname TEXT,
            device_name TEXT,
            device_type TEXT,
            first_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_seen DATETIME DEFAULT CURRENT_TIMESTAMP,
            is_monitored BOOLEAN DEFAULT 1,
            notes TEXT
        )
    ''')

    # Traffic statistics table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS traffic_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            src_ip TEXT NOT NULL,
            dst_ip TEXT NOT NULL,
            protocol TEXT,
            port INTEGER,
            bytes_sent INTEGER DEFAULT 0,
            packets_count INTEGER DEFAULT 1,
            duration_seconds INTEGER
        )
    ''')

    # System events table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS system_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            event_type TEXT NOT NULL,
            severity TEXT DEFAULT 'INFO',
            message TEXT NOT NULL,
            details TEXT,
            source_ip TEXT
        )
    ''')

    # Configuration table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS configuration (
            key TEXT PRIMARY KEY,
            value TEXT,
            description TEXT,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Insert default configuration
    default_config = [
        ('monitoring_enabled', 'true', 'Enable/disable monitoring'),
        ('log_level', 'INFO', 'Logging level'),
        ('retention_days', '30', 'Data retention period'),
        ('upstream_dns', '8.8.8.8,8.8.4.4', 'Upstream DNS servers'),
        ('web_port', '5000', 'Web dashboard port'),
        ('classification_enabled', 'false', 'AI classification enabled'),
    ]

    cursor.executemany(
        'INSERT OR IGNORE INTO configuration (key, value, description) VALUES (?, ?, ?)',
        default_config
    )

    # Create views for common queries
    cursor.execute('''
        CREATE VIEW IF NOT EXISTS recent_requests AS
        SELECT 
            dr.*,
            d.device_name,
            d.device_type
        FROM dns_requests dr
        LEFT JOIN devices d ON dr.client_ip = d.ip_address
        WHERE dr.timestamp > datetime('now', '-24 hours')
        ORDER BY dr.timestamp DESC
    ''')

    cursor.execute('''
        CREATE VIEW IF NOT EXISTS daily_stats AS
        SELECT 
            DATE(timestamp) as date,
            COUNT(*) as total_requests,
            COUNT(DISTINCT client_ip) as active_devices,
            COUNT(DISTINCT domain) as unique_domains
        FROM dns_requests
        GROUP BY DATE(timestamp)
        ORDER BY date DESC
    ''')

    # Commit changes and close connection
    conn.commit()
    conn.close()

    print(f"✅ Database created successfully at {db_path}")
    print("✅ Tables created: dns_requests, devices, traffic_stats, system_events, configuration")
    print("✅ Views created: recent_requests, daily_stats")

if __name__ == '__main__':
    create_database()

import time
import sqlite3
import re
from datetime import datetime

LOG_FILE = "/var/log/dnsmasq.log"
DB_FILE = "/home/pi/smartguard-monitor/data/dns_logs.db"

def parse_dns_log_line(line):
    match = re.search(r"^(\w+ \d+ \d+:\d+:\d+).*query\[(\w+)\] (\S+) from (\S+)", line)
    if match:
        log_time_str, record_type, domain, src_ip = match.groups()

        # Create datetime object with current year
        dt = datetime.strptime(f"{datetime.now().year} {log_time_str}", "%Y %b %d %H:%M:%S")

        # Format correctly for SQLite compatibility
        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")

        return (timestamp, src_ip, domain, record_type, "0")
    return None


def monitor_dns_log():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    with open(LOG_FILE, "r") as f:
        # Seek to end of file
        f.seek(0, 2)

        while True:
            line = f.readline()
            if not line:
                time.sleep(0.5)
                continue

            parsed = parse_dns_log_line(line)
            if parsed:
                cursor.execute('''
                    INSERT INTO dns_logs (timestamp, source_ip, queried_domain, record_type, response_code)
                    VALUES (?, ?, ?, ?, ?)
                ''', parsed)
                conn.commit()

if __name__ == "__main__":
    monitor_dns_log()

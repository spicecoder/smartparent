import sqlite3
from scapy.all import sniff, DNSQR
from datetime import datetime

DB_PATH = '/home/pi/smartguard-monitor/data/smartguard.db'

def log_query(client_ip, query_name):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            c = conn.cursor()
            c.execute('''
                INSERT INTO dns_requests (timestamp, client_ip, domain)
                VALUES (?, ?, ?)
            ''', (datetime.now(), client_ip, query_name))
            conn.commit()
    except Exception as e:
        print(f"[DB ERROR] {e}")


def process_packet(packet):
    if packet.haslayer(DNSQR):
        client_ip = packet[0].src  # source IP of query
        query_name = packet[DNSQR].qname.decode(errors="ignore")
        print(f"Query from {client_ip}: {query_name}")
        log_query(client_ip, query_name)

if __name__ == "__main__":
    print("Starting DNS monitor... (press Ctrl+C to stop)")
    sniff(filter="udp port 53", prn=process_packet, store=0)

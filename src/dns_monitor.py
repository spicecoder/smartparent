#!/usr/bin/env python3
import socket
import struct
import sqlite3
import threading
import time
import logging
from datetime import datetime
from typing import Optional, Tuple

class DNSMonitor:
    def __init__(self, db_path: str = '../data/smartguard.db'):
        self.db_path = db_path
        self.running = False
        self.socket = None
        # Setup logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('../logs/dns_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def parse_dns_query(self, data: bytes) -> Optional[str]:
        """Parse DNS query packet and extract domain name"""
        try:
            if len(data) < 12:
                return None

            domain_parts = []
            i = 12  # Skip DNS header

            while i < len(data):
                length = data[i]
                if length == 0:
                    break
                if length > 63:
                    break
                i += 1
                label = data[i:i+length].decode('utf-8', errors='ignore')
                domain_parts.append(label)
                i += length

            if domain_parts:
                domain = '.'.join(domain_parts)
                return domain.lower()
        except Exception as e:
            self.logger.error(f"Error parsing DNS query: {e}")
        return None

    def log_dns_request(self, client_ip: str, domain: str, query_type: str = 'A'):
        """Log DNS request to database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO dns_requests (client_ip, domain, query_type)
                VALUES (?, ?, ?)
            ''', (client_ip, domain, query_type))
            conn.commit()
            conn.close()
            self.logger.info(f"📡 DNS: {client_ip} -> {domain}")
        except Exception as e:
            self.logger.error(f"Database error: {e}")

    def forward_dns_request(self, data: bytes, upstream_dns: str = '8.8.8.8') -> Optional[bytes]:
        """Forward DNS request to upstream server"""
        try:
            upstream_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            upstream_socket.settimeout(5)
            upstream_socket.sendto(data, (upstream_dns, 53))
            response, _ = upstream_socket.recvfrom(512)
            upstream_socket.close()
            return response
        except Exception as e:
            self.logger.error(f"Upstream DNS error: {e}")
            return None

    def handle_dns_request(self, data: bytes, client_addr: Tuple[str, int]) -> Optional[bytes]:
        """Handle incoming DNS request"""
        client_ip = client_addr[0]
        domain = self.parse_dns_query(data)
        if domain:
            self.log_dns_request(client_ip, domain)
        response = self.forward_dns_request(data)
        return response

    def start_monitoring(self, bind_ip: str = '0.0.0.0', port: int = 53):
        """Start DNS monitoring service"""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.socket.bind((bind_ip, port))

            self.running = True
            self.logger.info(f"🚀 DNS Monitor started on {bind_ip}:{port}")

            while self.running:
                try:
                    data, client_addr = self.socket.recvfrom(512)

                    # Handle in separate thread
                    thread = threading.Thread(
                        target=self._handle_request_thread,
                        args=(data, client_addr)
                    )
                    thread.daemon = True
                    thread.start()

                except socket.timeout:
                    continue
                except Exception as e:
                    if self.running:
                        self.logger.error(f"Socket error: {e}")

        except Exception as e:
            self.logger.error(f"Failed to start DNS monitor: {e}")
        finally:
            self.stop_monitoring()

    def _handle_request_thread(self, data: bytes, client_addr: Tuple[str, int]):
        try:
            response = self.handle_dns_request(data, client_addr)
            if response and self.socket:
                self.socket.sendto(response, client_addr)
        except Exception as e:
            self.logger.error(f"Error handling DNS request: {e}")

    def stop_monitoring(self):
        """Stop DNS monitoring service"""
        self.running = False
        if self.socket:
            self.socket.close()
        self.logger.info("🛑 DNS Monitor stopped")


def main():
    import os
    os.makedirs('../logs', exist_ok=True)
    monitor = DNSMonitor()
    try:
        # Port 53 requires root privileges
        monitor.start_monitoring(bind_ip='0.0.0.0', port=53)
    except KeyboardInterrupt:
        print("\n🛑 Stopping DNS monitor...")
        monitor.stop_monitoring()


if __name__ == '__main__':
    main()

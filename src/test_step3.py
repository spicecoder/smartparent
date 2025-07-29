#!/usr/bin/env python3
from domain_classifier import DomainClassifier
import sqlite3
import time

def test_classification():
    print("🔍 Testing domain classification...")
    classifier = DomainClassifier()
    test_domains = ['facebook.com', 'khanacademy.org', 'pornhub.com', 'minecraft.net', 'google.com']
    for domain in test_domains:
        result = classifier.classify_domain(domain)
        print(f"{domain}: {result['category']} ({result['confidence']})")

def test_cache_speed():
    print("\n⚡ Testing classification cache speed...")
    classifier = DomainClassifier()
    domain = "facebook.com"
    start = time.time()
    classifier.classify_domain(domain)
    first_duration = time.time() - start

    start = time.time()
    classifier.classify_domain(domain)
    second_duration = time.time() - start

    print(f"1st request: {first_duration:.2f}s")
    print(f"2nd request (cached): {second_duration:.2f}s")

def test_database():
    print("\n📊 Testing database tables...")
    conn = sqlite3.connect("../data/smartguard.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    required = ['domain_classifications', 'alert_rules', 'alerts']
    for table in required:
        print(f"{'✅' if table in tables else '❌'} {table}")
    conn.close()

if __name__ == "__main__":
    test_classification()
    test_cache_speed()
    test_database()

#!/usr/bin/env python3
import subprocess
import time
import requests
import sqlite3

def test_database():
    try:
        conn = sqlite3.connect('data/smartguard.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM dns_requests")
        count = cursor.fetchone()[0]
        conn.close()
        print(f"✅ Database: {count} DNS requests logged")
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def test_web_dashboard():
    try:
        response = requests.get('http://localhost:5000', timeout=5)
        if response.status_code == 200:
            print("✅ Web dashboard: Accessible")
            return True
        else:
            print(f"❌ Web dashboard: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Web dashboard error: {e}")
        return False

def test_dns_resolution():
    try:
        result = subprocess.run(['nslookup', 'google.com', '127.0.0.1'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ DNS resolution: Working")
            return True
        else:
            print(f"❌ DNS resolution failed: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ DNS resolution error: {e}")
        return False

def main():
    print("🧪 Testing SmartGuard System")
    print("=" * 40)

    tests = [
        ("Database", test_database),
        ("Web Dashboard", test_web_dashboard),
        ("DNS Resolution", test_dns_resolution)
    ]

    passed = 0
    for name, test_func in tests:
        print(f"\nTesting {name}...")
        if test_func():
            passed += 1
        time.sleep(1)

    print("\n" + "=" * 40)
    print(f"Tests completed: {passed}/{len(tests)} passed")

    if passed == len(tests):
        print("🎉 All tests passed! System is ready.")
    else:
        print("⚠️ Some tests failed. Check configuration.")

if __name__ == '__main__':
    main()

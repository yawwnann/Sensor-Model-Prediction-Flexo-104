"""
test_connection.py
Script untuk testing koneksi database
"""

import os
from dotenv import load_dotenv
import psycopg2

# Load environment variables
load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    print("✗ DATABASE_URL tidak ditemukan di file .env")
    exit(1)

print("="*70)
print("DATABASE CONNECTION TEST")
print("="*70)

print(f"\n[INFO] DATABASE_URL: {DATABASE_URL[:50]}...")

# Test 1: Basic Connection
print("\n[TEST 1] Testing basic connection...")
try:
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
    print("✓ Koneksi berhasil!")
    conn.close()
except Exception as e:
    print(f"✗ Koneksi gagal: {e}")
    exit(1)

# Test 2: Query Components Table
print("\n[TEST 2] Testing components table query...")
try:
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM components;")
    results = cursor.fetchall()
    print(f"✓ Query berhasil! Ditemukan {len(results)} komponen:")
    for row in results:
        print(f"  - ID: {row[0]}, Name: {row[1]}, RPN: {row[2]}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"✗ Query gagal: {e}")
    exit(1)

# Test 3: Test MAX RPN Query
print("\n[TEST 3] Testing MAX RPN query...")
try:
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(rpn_value) FROM components;")
    result = cursor.fetchone()
    max_rpn = result[0]
    print(f"✓ MAX RPN value: {max_rpn}")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"✗ Query gagal: {e}")
    exit(1)

# Test 4: Test Specific Component Query
print("\n[TEST 4] Testing specific component query...")
try:
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT rpn_value FROM components WHERE name = %s", ("Pre-Feeder",))
    result = cursor.fetchone()
    if result:
        print(f"✓ Pre-Feeder RPN value: {result[0]}")
    else:
        print("✗ Pre-Feeder tidak ditemukan")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"✗ Query gagal: {e}")
    exit(1)

print("\n" + "="*70)
print("✓ SEMUA TEST BERHASIL!")
print("="*70 + "\n")

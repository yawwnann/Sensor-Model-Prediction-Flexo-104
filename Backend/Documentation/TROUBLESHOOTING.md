# Troubleshooting Guide - FlexoTwin Backend API

## Error: Connection Timed Out (IPv6 Issue)

### Gejala:
```
Error koneksi database: connection to server at "db.puqyxetcywvedkynmimd.supabase.co" 
(2406:da18:243:7424:7ab7:dfbe:1495:364d), port 5432 failed: Connection timed out
```

### Penyebab:
- Firewall memblokir koneksi IPv6
- ISP tidak mendukung IPv6
- Supabase server menggunakan IPv6 address

### Solusi:

#### **Solusi 1: Gunakan IPv4 Address (Recommended)**

1. Buka Supabase Dashboard
2. Pergi ke Settings → Database
3. Cari "Connection String" atau "Connection Info"
4. Gunakan **IPv4 address** bukan IPv6

Contoh DATABASE_URL yang benar:
```env
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@db.puqyxetcywvedkynmimd.supabase.co:5432/postgres"
```

#### **Solusi 2: Disable IPv6 di Windows**

Jika Anda menggunakan Windows dan ingin disable IPv6:

1. Buka Command Prompt sebagai Administrator
2. Jalankan:
```cmd
netsh int ipv6 set state disabled
```

3. Restart komputer

Untuk enable kembali:
```cmd
netsh int ipv6 set state enabled
```

#### **Solusi 3: Gunakan SSH Tunnel (Advanced)**

Jika kedua solusi di atas tidak berhasil, gunakan SSH tunnel:

1. Install `sshtunnel`:
```bash
pip install sshtunnel
```

2. Modifikasi `app.py` untuk menggunakan SSH tunnel (lihat contoh di bawah)

#### **Solusi 4: Gunakan Connection Pooling**

Install `psycopg2-pool`:
```bash
pip install psycopg2-binary
```

Modifikasi `app.py`:
```python
from psycopg2 import pool

# Buat connection pool
connection_pool = pool.SimpleConnectionPool(1, 20, DATABASE_URL)

def get_db_connection():
    return connection_pool.getconn()

def return_db_connection(conn):
    connection_pool.putconn(conn)
```

---

## Error: "relation 'components' does not exist"

### Penyebab:
Tabel `components` belum dibuat di database Supabase

### Solusi:

1. Buka Supabase Dashboard
2. Pergi ke SQL Editor
3. Jalankan query berikut:

```sql
CREATE TABLE components (
  id SERIAL PRIMARY KEY,
  name VARCHAR(255) UNIQUE NOT NULL,
  rpn_value INT NOT NULL
);

INSERT INTO components (name, rpn_value) VALUES 
  ('Pre-Feeder', 168), 
  ('Feeder', 192), 
  ('Printing', 162), 
  ('Slotter', 144), 
  ('Stacker', 54);
```

4. Verifikasi tabel dibuat dengan query:
```sql
SELECT * FROM components;
```

---

## Error: "DATABASE_URL tidak ditemukan di file .env"

### Penyebab:
File `.env` tidak ada atau tidak di-load dengan benar

### Solusi:

1. Pastikan file `.env` ada di folder `backend/`
2. Pastikan format benar:
```env
DATABASE_URL="postgresql://postgres:PASSWORD@HOST:5432/postgres"
```

3. Jangan ada spasi sebelum atau sesudah `=`
4. Restart server Flask

---

## Error: "psycopg2.OperationalError: FATAL: password authentication failed"

### Penyebab:
Password database salah atau tidak sesuai

### Solusi:

1. Buka Supabase Dashboard
2. Pergi ke Settings → Database
3. Klik "Reset password" untuk reset password database
4. Copy password baru
5. Update DATABASE_URL di file `.env`:
```env
DATABASE_URL="postgresql://postgres:NEW_PASSWORD@db.xxx.supabase.co:5432/postgres"
```

6. Restart server

---

## Error: "Connection refused" atau "Connection reset by peer"

### Penyebab:
- Database Supabase sedang down
- Firewall memblokir port 5432
- Network connectivity issue

### Solusi:

1. **Cek status Supabase:**
   - Buka https://status.supabase.com
   - Pastikan tidak ada incident

2. **Cek firewall:**
   - Windows Defender Firewall
   - Third-party antivirus
   - ISP firewall

3. **Test koneksi dengan psql:**
```bash
psql -h db.xxx.supabase.co -U postgres -d postgres
```

4. **Cek network connectivity:**
```bash
ping db.xxx.supabase.co
```

---

## Error: "statement_timeout" atau "Query Timeout"

### Penyebab:
Query terlalu lama atau database overloaded

### Solusi:

1. Tingkatkan timeout di `app.py`:
```python
DB_CONNECTION_TIMEOUT = 30  # Ubah dari 10 ke 30 detik
```

2. Tambahkan index pada tabel:
```sql
CREATE INDEX idx_components_name ON components(name);
```

3. Optimalkan query

---

## Error: "too many connections"

### Penyebab:
Terlalu banyak koneksi database yang terbuka

### Solusi:

1. Pastikan koneksi ditutup di blok `finally`
2. Gunakan connection pooling
3. Kurangi jumlah concurrent requests

---

## Testing Koneksi Database

### Test 1: Cek DATABASE_URL
```python
import os
from dotenv import load_dotenv

load_dotenv()
print(os.getenv('DATABASE_URL'))
```

### Test 2: Test Koneksi Langsung
```python
import psycopg2

DATABASE_URL = "postgresql://postgres:PASSWORD@HOST:5432/postgres"

try:
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
    print("✓ Koneksi berhasil!")
    conn.close()
except Exception as e:
    print(f"✗ Koneksi gagal: {e}")
```

### Test 3: Test Query
```python
import psycopg2

DATABASE_URL = "postgresql://postgres:PASSWORD@HOST:5432/postgres"

try:
    conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM components;")
    results = cursor.fetchall()
    print(f"✓ Query berhasil! Ditemukan {len(results)} komponen")
    cursor.close()
    conn.close()
except Exception as e:
    print(f"✗ Query gagal: {e}")
```

---

## Debugging Tips

### 1. Enable Verbose Logging
Tambahkan di `app.py`:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 2. Print Debug Info
```python
print(f"[DEBUG] DATABASE_URL: {DATABASE_URL[:50]}...")
print(f"[DEBUG] Connection attempt: {attempt + 1}/{DB_RETRY_ATTEMPTS}")
```

### 3. Monitor Network Traffic
Gunakan Wireshark untuk monitor traffic ke Supabase

### 4. Check Supabase Logs
- Buka Supabase Dashboard
- Pergi ke Logs
- Cari error messages

---

## Checklist Troubleshooting

- [ ] DATABASE_URL benar dan lengkap
- [ ] Password database benar
- [ ] Tabel `components` sudah dibuat
- [ ] File `.env` ada di folder `backend/`
- [ ] Koneksi internet stabil
- [ ] Firewall tidak memblokir port 5432
- [ ] Supabase server tidak down
- [ ] IPv6 tidak menjadi masalah
- [ ] Timeout cukup (minimal 10 detik)
- [ ] Koneksi ditutup dengan benar

---

## Hubungi Support

Jika masalah masih berlanjut:

1. **Supabase Support**: https://supabase.com/support
2. **PostgreSQL Documentation**: https://www.postgresql.org/docs/
3. **psycopg2 Documentation**: https://www.psycopg.org/

---

## Contoh DATABASE_URL yang Benar

```env
# Format umum
DATABASE_URL="postgresql://user:password@host:port/database"

# Contoh Supabase
DATABASE_URL="postgresql://postgres:abc123xyz@db.puqyxetcywvedkynmimd.supabase.co:5432/postgres"

# Dengan SSL
DATABASE_URL="postgresql://postgres:abc123xyz@db.puqyxetcywvedkynmimd.supabase.co:5432/postgres?sslmode=require"
```

---

Last Updated: October 2025

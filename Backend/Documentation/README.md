# FlexoTwin Smart Maintenance 4.0 - Backend API

Backend API untuk sistem monitoring kesehatan mesin Flexo dengan integrasi database PostgreSQL (Supabase).

## 📋 Daftar Isi

- [Quick Start](#quick-start)
- [Struktur Proyek](#struktur-proyek)
- [Setup & Instalasi](#setup--instalasi)
- [API Endpoints](#api-endpoints)
- [Kalkulasi Health Index](#kalkulasi-health-index)
- [Testing](#testing)
- [Troubleshooting](#troubleshooting)

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup Environment
Edit `.env`:
```env
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@db.xxx.supabase.co:5432/postgres"
```

### 3. Setup Database
Jalankan SQL di Supabase SQL Editor:
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

### 4. Run Server
```bash
python app.py
```

### 5. Test API
```bash
curl http://localhost:5000/api/health/Pre-Feeder
```

## 📁 Struktur Proyek

```
backend/
├── app.py                    # Main Flask application
├── config.py                 # Konfigurasi aplikasi
├── database.py               # Database operations
├── health_calculator.py      # Business logic kalkulasi
├── routes.py                 # API endpoints
├── test_connection.py        # Testing script
├── .env                      # Environment variables
├── requirements.txt          # Dependencies
├── README.md                 # Dokumentasi ini
├── TROUBLESHOOTING.md        # Panduan troubleshooting
└── PROJECT_STRUCTURE.md      # Detail struktur proyek
```

Lihat [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) untuk penjelasan detail setiap file.

## 🔧 Setup & Instalasi

### Prerequisites
- Python 3.8+
- PostgreSQL (Supabase)
- pip

### Step 1: Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

Atau install manual:
```bash
pip install Flask psycopg2-binary python-dotenv
```

### Step 2: Konfigurasi Database

1. Buka Supabase Dashboard
2. Pergi ke Settings → Database
3. Copy PostgreSQL Connection String
4. Edit file `.env`:
```env
DATABASE_URL="postgresql://postgres:YOUR_PASSWORD@db.puqyxetcywvedkynmimd.supabase.co:5432/postgres"
```

### Step 3: Setup Database

Jalankan query SQL di Supabase SQL Editor:

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

### Step 4: Test Koneksi

```bash
python test_connection.py
```

Output yang diharapkan:
```
======================================================================
DATABASE CONNECTION TEST
======================================================================

[INFO] DATABASE_URL: postgresql://postgres:***@db.xxx.supabase.co:5432/postgres...

[TEST 1] Testing basic connection...
✓ Koneksi berhasil!

[TEST 2] Testing components table query...
✓ Query berhasil! Ditemukan 5 komponen:
  - ID: 1, Name: Pre-Feeder, RPN: 168
  - ID: 2, Name: Feeder, RPN: 192
  ...

[TEST 3] Testing MAX RPN query...
✓ MAX RPN value: 192

[TEST 4] Testing specific component query...
✓ Pre-Feeder RPN value: 168

======================================================================
✓ SEMUA TEST BERHASIL!
======================================================================
```

### Step 5: Jalankan Server

```bash
python app.py
```

Output:
```
======================================================================
FlexoTwin Smart Maintenance 4.0
Version: 1.0.0
======================================================================

[STARTUP] Testing database connection...
[SUCCESS] Database connection test passed!

✓ Server dimulai...
✓ Database: PostgreSQL (Supabase)
✓ Akses API di: http://0.0.0.0:5000

Endpoint yang tersedia:
  • GET /api/health                              - Health check umum
  • GET /api/components                          - Daftar semua komponen
  • GET /api/health/<component_name>             - Health check komponen
  • GET /api/components/<component_name>/health  - Detail health komponen

Contoh:
  • http://localhost:5000/api/health/Pre-Feeder
  • http://localhost:5000/api/components/Printing/health

Tekan CTRL+C untuk menghentikan server.

======================================================================
```

## 📡 API Endpoints

### 1. Health Check Umum
**Endpoint:** `GET /api/health`

**Response:**
```json
{
  "status": "API Server Running",
  "service": "FlexoTwin Smart Maintenance 4.0",
  "version": "1.0.0",
  "database": "PostgreSQL (Supabase)"
}
```

### 2. Daftar Semua Komponen
**Endpoint:** `GET /api/components`

**Response:**
```json
{
  "components": [
    {
      "id": 1,
      "name": "Pre-Feeder",
      "rpnValue": 168
    },
    {
      "id": 2,
      "name": "Feeder",
      "rpnValue": 192
    }
  ],
  "total": 5
}
```

### 3. Health Check Komponen
**Endpoint:** `GET /api/health/<component_name>`

**Contoh:** `GET /api/health/Pre-Feeder`

**Response (Success):**
```json
{
  "componentName": "Pre-Feeder",
  "healthIndex": 75.42,
  "status": "Sehat",
  "color": "#00FF00",
  "description": "Kondisi mesin normal, perhatikan tren penurunan",
  "metrics": {
    "rpnScore": 20.0,
    "oeeScore": 92.5,
    "rpnValue": 168,
    "rpnMax": 192
  }
}
```

**Response (Not Found):**
```json
{
  "error": "Komponen tidak ditemukan",
  "component": "InvalidComponent",
  "message": "Komponen 'InvalidComponent' tidak ada di database"
}
```

### 4. Detail Health Komponen
**Endpoint:** `GET /api/components/<component_name>/health`

**Contoh:** `GET /api/components/Pre-Feeder/health`

**Response:**
```json
{
  "component": {
    "name": "Pre-Feeder",
    "rpnValue": 168,
    "rpnMax": 192
  },
  "health": {
    "index": 75.42,
    "status": "Sehat",
    "color": "#00FF00",
    "description": "Kondisi mesin normal, perhatikan tren penurunan"
  },
  "metrics": {
    "rpnScore": {
      "value": 20.0,
      "weight": 0.4,
      "description": "Risk Priority Number Score"
    },
    "oeeScore": {
      "value": 92.5,
      "weight": 0.6,
      "description": "Overall Equipment Effectiveness Score"
    }
  },
  "calculation": {
    "formula": "(RPN_Score * 0.4) + (OEE_Score * 0.6)",
    "result": "(20.0 * 0.4) + (92.5 * 0.6) = 75.42"
  }
}
```

## 📊 Kalkulasi Health Index

### Formula

```
RPN Score = (1 - RPN_Value / RPN_Max) * 100
OEE Score = Random(85.0, 99.5)
Final Health Index = (RPN_Score * 0.4) + (OEE_Score * 0.6)
```

### Penjelasan

- **RPN Score (40%)**: Risk Priority Number dari FMEA analysis
  - Semakin rendah RPN, semakin tinggi score
  - Range: 0-100

- **OEE Score (60%)**: Overall Equipment Effectiveness
  - Simulasi data real-time
  - Range: 85.0-99.5

- **Final Health Index**: Kombinasi weighted
  - Range: 0-100
  - Threshold: >= 70 = Sehat, < 70 = Perlu Perhatian

### Status Kesehatan

| Health Index | Status | Warna | Deskripsi |
|---|---|---|---|
| >= 90 | Sehat | 🟢 Green | Sangat baik, tidak ada tindakan |
| 80-89 | Sehat | 🟢 Green | Baik, lakukan monitoring rutin |
| 70-79 | Sehat | 🟢 Light Green | Normal, perhatikan tren |
| 50-69 | Perlu Perhatian | 🟠 Orange | Perlu perhatian, rencanakan maintenance |
| < 50 | Kritis | 🔴 Red | Kritis, lakukan maintenance segera |

## 🧪 Testing

### Test Database Connection
```bash
python test_connection.py
```

### Test API dengan cURL

```bash
# Health check umum
curl http://localhost:5000/api/health

# Daftar komponen
curl http://localhost:5000/api/components

# Health check Pre-Feeder
curl http://localhost:5000/api/health/Pre-Feeder

# Detail health Pre-Feeder
curl http://localhost:5000/api/components/Pre-Feeder/health

# Health check Printing
curl http://localhost:5000/api/health/Printing
```

### Test API dengan Python

```python
import requests

# Health check umum
response = requests.get('http://localhost:5000/api/health')
print(response.json())

# Health check komponen
response = requests.get('http://localhost:5000/api/health/Pre-Feeder')
print(response.json())

# Detail health
response = requests.get('http://localhost:5000/api/components/Pre-Feeder/health')
print(response.json())
```

## 🐛 Troubleshooting

Lihat [TROUBLESHOOTING.md](TROUBLESHOOTING.md) untuk panduan lengkap troubleshooting.

### Error Umum

**Error: Connection Timed Out**
- Gunakan IPv4 address di Supabase
- Disable IPv6 di Windows
- Lihat TROUBLESHOOTING.md untuk solusi detail

**Error: DATABASE_URL tidak ditemukan**
- Pastikan file `.env` ada di folder `backend/`
- Pastikan format DATABASE_URL benar

**Error: relation 'components' does not exist**
- Jalankan SQL query untuk membuat tabel
- Pastikan Anda menjalankan query di database yang benar

## 📚 Dokumentasi Tambahan

- [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) - Detail struktur proyek
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Panduan troubleshooting
- [Flask Documentation](https://flask.palletsprojects.com/)
- [psycopg2 Documentation](https://www.psycopg.org/)
- [Supabase Documentation](https://supabase.com/docs)

## 🔐 Security Notes

- Jangan commit file `.env` ke git
- Gunakan environment variables untuk sensitive data
- Enable SSL/TLS untuk production
- Implement authentication & authorization
- Validate semua input dari user

## 📝 License

MIT

## 👤 Author

Yuwananta

---

**Last Updated:** October 2025

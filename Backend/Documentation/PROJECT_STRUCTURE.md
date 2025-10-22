# Project Structure - FlexoTwin Backend

## Struktur Folder

```
backend/
├── app.py                    # Main Flask application (entry point)
├── config.py                 # Konfigurasi aplikasi dan database
├── database.py               # Fungsi-fungsi database operations
├── health_calculator.py      # Fungsi-fungsi kalkulasi health index
├── routes.py                 # Definisi semua API endpoints
├── test_connection.py        # Script untuk testing koneksi database
├── .env                      # Environment variables (DATABASE_URL)
├── requirements.txt          # Daftar dependensi Python
├── README.md                 # Dokumentasi proyek
├── TROUBLESHOOTING.md        # Panduan troubleshooting
└── PROJECT_STRUCTURE.md      # File ini
```

## Penjelasan File

### `app.py` (Main Application)
- Entry point aplikasi Flask
- Membuat Flask app instance
- Register blueprints
- Test database connection saat startup
- Menjalankan server

**Tanggung Jawab:**
- Inisialisasi aplikasi
- Konfigurasi Flask
- Startup dan shutdown

### `config.py` (Configuration)
- Menyimpan semua konfigurasi aplikasi
- Load environment variables dari `.env`
- Definisi konstanta dan parameter

**Konfigurasi yang tersedia:**
- Database connection parameters
- Flask configuration
- Application info
- Health index weights
- Logging configuration

### `database.py` (Database Operations)
- Fungsi-fungsi untuk koneksi database
- Query operations
- Connection pooling dan retry logic
- Error handling

**Fungsi utama:**
- `get_db_connection()` - Koneksi dengan retry logic
- `get_rpn_value_from_db()` - Ambil RPN value komponen
- `get_all_components_from_db()` - Ambil semua komponen
- `test_database_connection()` - Test koneksi

### `health_calculator.py` (Business Logic)
- Kalkulasi health index
- Simulasi OEE score
- Penentuan status kesehatan
- Utility functions untuk UI

**Fungsi utama:**
- `calculate_rpn_score()` - Hitung RPN score
- `generate_oee_score()` - Generate OEE score
- `calculate_final_health_index()` - Hitung final health index
- `determine_health_status()` - Tentukan status
- `get_health_color()` - Warna untuk UI
- `get_health_description()` - Deskripsi status

### `routes.py` (API Endpoints)
- Definisi semua API endpoints
- Request handling
- Response formatting
- Error handlers

**Endpoints:**
- `GET /api/health` - Health check umum
- `GET /api/components` - Daftar komponen
- `GET /api/health/<component_name>` - Health check komponen
- `GET /api/components/<component_name>/health` - Detail health

### `test_connection.py` (Testing)
- Script untuk testing koneksi database
- Verifikasi konfigurasi
- Test queries

**Test yang dilakukan:**
- Basic connection test
- Components table query
- MAX RPN query
- Specific component query

### `.env` (Environment Variables)
```env
DATABASE_URL="postgresql://postgres:PASSWORD@HOST:5432/postgres"
```

### `requirements.txt` (Dependencies)
```
Flask==3.0.3
psycopg2-binary==2.9.9
python-dotenv==1.0.0
Werkzeug==3.0.3
```

## Alur Eksekusi

### Startup
```
app.py
  ├── Load config.py
  ├── Test database connection
  ├── Create Flask app
  ├── Register routes.py blueprint
  └── Run server
```

### Request Flow
```
Request ke /api/health/<component_name>
  ├── routes.py (get_component_health)
  ├── database.py (get_rpn_value_from_db)
  ├── health_calculator.py (calculate_component_health)
  └── Return JSON response
```

## Maintenance Guide

### Menambah Endpoint Baru
1. Buka `routes.py`
2. Tambahkan fungsi endpoint baru
3. Dekorasi dengan `@api_bp.route()`
4. Restart server

### Mengubah Kalkulasi Health Index
1. Buka `health_calculator.py`
2. Modifikasi fungsi kalkulasi
3. Update `config.py` jika ada konstanta baru
4. Test dengan `test_connection.py`

### Menambah Konfigurasi Baru
1. Buka `config.py`
2. Tambahkan konstanta baru
3. Load dari environment variable jika perlu
4. Import di file yang membutuhkan

### Menambah Database Query
1. Buka `database.py`
2. Tambahkan fungsi query baru
3. Gunakan di `routes.py`
4. Test dengan `test_connection.py`

## Best Practices

### 1. Separation of Concerns
- `app.py` - Application setup
- `config.py` - Configuration
- `database.py` - Data access
- `health_calculator.py` - Business logic
- `routes.py` - API endpoints

### 2. Error Handling
- Semua database operations di-wrap dengan try-except
- Connection selalu ditutup di finally block
- Error messages yang informatif

### 3. Logging
- Gunakan print statements dengan prefix [INFO], [ERROR], [WARNING]
- Catat setiap request dan response
- Log database operations

### 4. Configuration Management
- Semua konstanta di `config.py`
- Environment variables di `.env`
- Jangan hardcode values

### 5. Code Organization
- Satu file untuk satu tanggung jawab
- Fungsi-fungsi yang reusable
- Clear naming conventions

## Testing

### Test Database Connection
```bash
python test_connection.py
```

### Test API Endpoints
```bash
# Health check
curl http://localhost:5000/api/health

# Get components
curl http://localhost:5000/api/components

# Get component health
curl http://localhost:5000/api/health/Pre-Feeder

# Get component detail health
curl http://localhost:5000/api/components/Pre-Feeder/health
```

## Deployment

### Production Setup
1. Set `FLASK_ENV=production` di `.env`
2. Gunakan production WSGI server (Gunicorn, uWSGI)
3. Setup reverse proxy (Nginx)
4. Enable SSL/TLS
5. Setup logging dan monitoring

### Example Gunicorn Command
```bash
gunicorn -w 4 -b 0.0.0.0:5000 app:create_app()
```

## Future Improvements

- [ ] Add database connection pooling
- [ ] Add caching layer (Redis)
- [ ] Add authentication & authorization
- [ ] Add API rate limiting
- [ ] Add comprehensive logging
- [ ] Add unit tests
- [ ] Add API documentation (Swagger)
- [ ] Add monitoring & alerting
- [ ] Add data export (CSV, Excel)
- [ ] Add real-time updates (WebSocket)

---

Last Updated: October 2025

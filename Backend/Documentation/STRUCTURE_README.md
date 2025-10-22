# 📁 Backend Structure Overview

Struktur backend telah dirapikan menggunakan **layered architecture pattern** untuk maintainability dan scalability yang lebih baik.

## 🏗️ **Struktur Direktori Baru**

```
Backend/
├── 📄 app.py                          # Main Flask application entry point
├── 📄 config.py                       # Configuration management
├── 📄 requirements.txt                # Dependencies with CORS support
├── 📄 .env                           # Environment variables (database, etc.)
│
├── 📂 src/                           # Source code directory
│   ├── 📂 controllers/               # API endpoint controllers
│   │   ├── __init__.py
│   │   ├── routes.py                # Route registration & error handlers
│   │   ├── health_controller.py     # Health check endpoints
│   │   ├── component_controller.py  # Component management endpoints
│   │   ├── prediction_controller.py # ML prediction endpoints
│   │   └── docs_controller.py       # API documentation endpoint
│   │
│   ├── 📂 services/                  # Business logic layer
│   │   ├── __init__.py
│   │   ├── database_service.py      # Database operations with connection pooling
│   │   ├── health_service.py        # Health calculation logic
│   │   └── prediction_service.py    # ML prediction service
│   │
│   ├── 📂 models/                    # Data models (future use)
│   │   └── __init__.py
│   │
│   └── 📂 utils/                     # Utility functions
│       ├── __init__.py
│       └── logger.py                # Logging configuration
│
├── 📂 logs/                          # Application logs (auto-generated)
│   └── flexotwin_YYYY-MM-DD.log     # Daily log files
│
├── 📂 tests/                         # Unit tests (future use)
│
└── 📄 Legacy Files (Deprecated)      # Kept for compatibility
    ├── routes.py                     # → src/controllers/
    ├── database.py                   # → src/services/database_service.py
    ├── health_calculator.py          # → src/services/health_service.py
    └── predictor.py                  # → src/services/prediction_service.py
```

## 🔄 **Perubahan Utama**

### **1. Layered Architecture**

- **Controllers**: Handle HTTP requests/responses
- **Services**: Business logic dan data processing
- **Utils**: Utility functions dan helpers

### **2. Improved Error Handling**

- Centralized error handlers
- Structured error responses
- Better logging dengan daily log files

### **3. Enhanced API Documentation**

- Built-in API documentation endpoint: `GET /api/docs`
- Comprehensive response examples
- Usage guidelines dan troubleshooting

### **4. Better Logging System**

- Daily log files di folder `logs/`
- Structured logging dengan timestamps
- Different log levels (INFO, WARNING, ERROR)

### **5. CORS Support**

- Added Flask-CORS untuk frontend integration
- Configurable allowed origins

## 🚀 **Cara Menjalankan**

### **1. Install Dependencies**

```bash
cd Backend
pip install -r requirements.txt
```

### **2. Setup Environment**

Pastikan file `.env` berisi:

```env
DATABASE_URL=postgresql://user:password@host:port/database
FLASK_ENV=development
LOG_LEVEL=INFO
```

### **3. Start Server**

```bash
python app.py
```

## 📋 **API Endpoints**

### **Health Checks**

- `GET /api/health` - API health check
- `GET /api/health/<component_name>` - Component health

### **Components**

- `GET /api/components` - List all components
- `GET /api/components/<component_name>/health` - Detailed component health

### **Predictions**

- `POST /api/predict/maintenance` - Single prediction
- `POST /api/predict/maintenance/batch` - Batch predictions
- `GET /api/model/info` - Model information

### **Documentation**

- `GET /api/docs` - Complete API documentation

## 🔧 **Features Baru**

### **1. Enhanced Startup Info**

Server startup menampilkan informasi lengkap:

- Database connection status
- Available endpoints
- Usage examples
- Server configuration

### **2. Better Error Messages**

Error responses include:

- Descriptive error messages
- Troubleshooting tips
- Expected request formats
- Example requests

### **3. Comprehensive Logging**

- Request logging
- Error logging
- Performance logging
- Daily log rotation

### **4. Input Validation**

- Strict input validation untuk predictions
- Meaningful validation error messages
- Type checking dan range validation

## 🎯 **Benefits**

### **✅ Maintainability**

- Separation of concerns
- Clear code organization
- Easy to add new features

### **✅ Scalability**

- Modular structure
- Service-based architecture
- Easy to extend

### **✅ Developer Experience**

- Built-in API documentation
- Comprehensive error messages
- Better debugging dengan logs

### **✅ Production Ready**

- Proper error handling
- Logging system
- CORS configuration
- Input validation

## 🔄 **Migration Guide**

File-file lama masih ada untuk kompatibilitas, tapi sekarang menggunakan struktur baru:

- `routes.py` → `src/controllers/*.py`
- `database.py` → `src/services/database_service.py`
- `health_calculator.py` → `src/services/health_service.py`
- `predictor.py` → `src/services/prediction_service.py`

Import statements sudah diupdate di `app.py` untuk menggunakan struktur baru.

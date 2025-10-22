"""
config.py
Konfigurasi aplikasi Flask dan database
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============================================================================
# DATABASE CONFIGURATION
# ============================================================================
DATABASE_URL = os.getenv('DATABASE_URL')

if not DATABASE_URL:
    raise ValueError("DATABASE_URL tidak ditemukan di file .env")

# Database connection parameters
DB_CONNECTION_TIMEOUT = 10  # Timeout 10 detik
DB_RETRY_ATTEMPTS = 3       # Jumlah percobaan koneksi

# ============================================================================
# FLASK CONFIGURATION
# ============================================================================
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
DEBUG = FLASK_ENV == 'development'
HOST = '0.0.0.0'
PORT = 5000

# ============================================================================
# APPLICATION INFO
# ============================================================================
APP_NAME = "FlexoTwin Smart Maintenance 4.0"
APP_VERSION = "1.0.0"
APP_DESCRIPTION = "Backend API untuk monitoring kesehatan mesin Flexo"

# ============================================================================
# HEALTH INDEX CONFIGURATION
# ============================================================================
# Bobot untuk perhitungan health index
RPN_WEIGHT = 0.4      # RPN Score weight: 40%
OEE_WEIGHT = 0.6      # OEE Score weight: 60%

# Threshold untuk status kesehatan
HEALTH_THRESHOLD_GOOD = 70  # >= 70: Sehat, < 70: Perlu Perhatian

# OEE Score range (0-100, tanpa clamp artificial)
OEE_MIN = 0.0
OEE_MAX = 100.0

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FORMAT = '[%(levelname)s] %(asctime)s - %(name)s - %(message)s'

# ============================================================================
# CORS CONFIGURATION
# ============================================================================
ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",  # Vite default port
    "http://127.0.0.1:5173"
]

# ============================================================================
# API CONFIGURATION
# ============================================================================
API_PREFIX = "/api"
API_TITLE = "FlexoTwin API"
API_DESCRIPTION = "REST API untuk Digital Twin Smart Maintenance System"

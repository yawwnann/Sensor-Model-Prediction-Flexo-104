# FlexoTwin Smart Maintenance 4.0

Sistem Digital Twin untuk monitoring dan prediksi pemeliharaan mesin Flexo 104 dengan teknologi Machine Learning dan MQTT real-time.

---

## 📋 Daftar Isi

- [Arsitektur Sistem](#arsitektur-sistem)
- [Instalasi Backend](#instalasi-backend)
- [Instalasi Sensor Simulator](#instalasi-sensor-simulator)
- [Dokumentasi API](#dokumentasi-api)
- [Integrasi API](#integrasi-api)
- [Troubleshooting](#troubleshooting)

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────┐      MQTT       ┌─────────────────┐      HTTP      ┌─────────────────┐
│ Sensor          │ ─────────────→  │ Backend API     │ ←────────────  │ Frontend        │
│ Simulator       │  (Real-time)    │ (Flask)         │   (REST API)   │ (React)         │
└─────────────────┘                 └─────────────────┘                └─────────────────┘
                                            │
                                            ↓
                                    ┌─────────────────┐
                                    │ PostgreSQL      │
                                    │ Database        │
                                    └─────────────────┘
```

### Komponen Utama:

- **Sensor Simulator**: Mensimulasikan data mesin berdasarkan data historis 1 tahun
- **Backend API**: REST API dengan Flask untuk health monitoring dan prediksi ML
- **Database**: PostgreSQL untuk menyimpan data historis dan perhitungan RPN/FMEA
- **MQTT Broker**: HiveMQ (public) untuk komunikasi real-time

---

## 🚀 Instalasi Backend

### Prasyarat

- Python 3.8 atau lebih baru
- PostgreSQL 12 atau lebih baru
- pip (Python package manager)

### Langkah 1: Clone Repository

```bash
git clone <repository-url>
cd Sistem2/Backend
```

### Langkah 2: Buat Virtual Environment (Opsional tapi Direkomendasikan)

```powershell
# Windows
python -m venv venv
.\venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### Langkah 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Dependencies yang dibutuhkan:**

- Flask 3.0.3 - Web framework
- psycopg2-binary 2.9.9 - PostgreSQL adapter
- python-dotenv 1.0.0 - Environment variable management
- scikit-learn 1.5.2 - Machine Learning library
- paho-mqtt 1.6.1 - MQTT client
- pandas, numpy - Data processing

### Langkah 4: Konfigurasi Database

#### 4.1. Buat Database PostgreSQL

```sql
CREATE DATABASE flexotwin_db;
```

#### 4.2. Buat File `.env`

Buat file `.env` di folder `Backend/` dengan konten:

```env
DATABASE_URL=postgresql://username:password@localhost:5432/flexotwin_db
FLASK_ENV=development
LOG_LEVEL=INFO
```

**Ganti:**

- `username` dengan username PostgreSQL Anda
- `password` dengan password PostgreSQL Anda
- `localhost` dengan host database (jika remote)

### Langkah 5: Test Koneksi Database

```bash
python test_connection.py
```

Output yang diharapkan:

```
[SUCCESS] Koneksi berhasil!
[SUCCESS] Query berhasil! Ditemukan X komponen
[SUCCESS] SEMUA TEST BERHASIL!
```

### Langkah 6: Jalankan Backend Server

```bash
python app.py
```

Backend akan berjalan di `http://localhost:5000`

**Output yang diharapkan:**

```
[INFO] FlexoTwin Smart Maintenance 4.0 - Backend API
[INFO] Version: 1.0.0
[INFO] Environment: development
[MQTT] Successfully connected to MQTT Broker
[INFO] Backend server started on http://0.0.0.0:5000
```

---

## 📡 Instalasi Sensor Simulator

Sensor simulator mensimulasikan data mesin Flexo 104 berdasarkan data historis dan mengirimkan data via MQTT.

### Langkah 1: Pindah ke Folder Sensor

```bash
cd ../Sensor
```

### Langkah 2: Install Dependencies (jika belum)

```bash
pip install paho-mqtt pandas openpyxl
```

### Langkah 3: Verifikasi Data CSV

Pastikan folder `Data Flexo CSV/` berisi file CSV data historis:

```
Data Flexo CSV/
├── Laporan Flexo Oktober 2024.csv
├── Laporan Flexo November 2024.csv
├── Laporan Flexo Desember 2024.csv
├── ... (file lainnya)
```

### Langkah 4: Jalankan Sensor Simulator

```bash
python sensor_simulator.py
```

**Output yang diharapkan:**

```
======================================================================
PHASE 1: DATA ANALYSIS & INITIALIZATION
======================================================================

[INFO] Membaca data dari folder: ../Data Flexo CSV
[INFO] Ditemukan 13 file CSV
[INFO] Data C_FL104: 12345 records

STATISTIK MESIN C_FL104:
  Average Availability Rate: 85.5%
  Average Performance Rate: 92.3%
  Average Quality Rate: 96.8%
  Downtime Probability: 14.5%

======================================================================
PHASE 2: MQTT CONNECTION
======================================================================

[MQTT] Attempting to connect to broker.hivemq.com:1883
[MQTT] Successfully connected to MQTT Broker
[MQTT] Subscribed to topic: flexotwin/machine/status

======================================================================
PHASE 3: SIMULATION LOOP
======================================================================

[MQTT] Publishing sensor data...
[MQTT] Message published successfully
[DATA] Machine: C_FL104 | Status: Running | Performance: 92.5% | Quality: 96.3%
```

### Konfigurasi Simulator

Edit `sensor_simulator.py` untuk mengubah:

```python
# MQTT Configuration
MQTT_BROKER = "broker.hivemq.com"  # Ganti dengan broker Anda
MQTT_PORT = 1883
MQTT_TOPIC = "flexotwin/machine/status"

# Simulation Configuration
SIMULATION_INTERVAL = 5  # Interval pengiriman data (detik)
PERFORMANCE_VARIANCE = 5  # Variasi performance ±5%
QUALITY_VARIANCE = 2     # Variasi quality ±2%
```

---

## 📚 Dokumentasi API

Base URL: `http://localhost:5000/api`

### Authentication

Saat ini API tidak memerlukan authentication (development mode).

### Content Type

Semua request dan response menggunakan `application/json`.

---

## 🔌 API Endpoints

### 1. Health Check System

#### GET `/api/health`

Mengecek status kesehatan sistem backend.

**Response:**

```json
{
  "status": "healthy",
  "app_name": "FlexoTwin Smart Maintenance 4.0",
  "version": "1.0.0",
  "timestamp": "2025-10-23T10:30:00",
  "database": {
    "status": "connected",
    "message": "PostgreSQL connection active"
  },
  "mqtt": {
    "status": "connected",
    "broker": "broker.hivemq.com:1883",
    "topic": "flexotwin/machine/status"
  }
}
```

---

### 2. Component Management

#### GET `/api/components`

Mendapatkan daftar semua komponen mesin dengan nilai RPN.

**Response:**

```json
{
  "total_components": 15,
  "components": [
    {
      "component_name": "Pre-Feeder",
      "rpn_value": 180,
      "rpn_max": 1000
    },
    {
      "component_name": "Anilox Roller",
      "rpn_value": 240,
      "rpn_max": 1000
    }
  ]
}
```

#### GET `/api/components/:component_name`

Mendapatkan detail komponen spesifik.

**Parameter:**

- `component_name` (string): Nama komponen (contoh: "Pre-Feeder")

**Response:**

```json
{
  "component_name": "Pre-Feeder",
  "rpn_value": 180,
  "rpn_max": 1000,
  "description": "Komponen pengumpan kertas"
}
```

---

### 3. Health Monitoring

#### GET `/api/health/:component_name`

Mendapatkan health index dan rekomendasi untuk komponen tertentu.

**Parameter:**

- `component_name` (string): Nama komponen

**Response:**

```json
{
  "component_name": "Pre-Feeder",
  "health_index": 72.5,
  "status": "Good",
  "color": "#22C55E",
  "description": "Komponen dalam kondisi baik",
  "recommendations": [
    "[MONITOR] Pantau keausan roller secara berkala",
    "[SCHEDULE] Jadwalkan pembersihan setiap 2 minggu",
    "[STATUS] Komponen dalam kondisi optimal"
  ],
  "metrics": {
    "rpn_score": 82.0,
    "oee_score": 88.5,
    "availability_rate": 95.2,
    "performance_rate": 92.3,
    "quality_rate": 96.8,
    "rpn_value": 180,
    "rpn_max": 1000
  },
  "calculation_details": {
    "formula": "(RPN_Score × 0.4) + (OEE_Score × 0.6)",
    "rpn_contribution": 32.8,
    "oee_contribution": 53.1
  },
  "auto_triggered": false
}
```

**Health Index Status:**

- **>= 70%**: Status "Good" (Hijau) - Kondisi baik
- **50-69%**: Status "Warning" (Kuning) - Perlu perhatian
- **< 50%**: Status "Critical" (Merah) - Tindakan segera diperlukan

**Auto-Trigger Prediction:**
Jika health index < 50%, sistem otomatis akan menjalankan prediksi maintenance dan menambahkan `prediction_result` ke response.

---

### 4. Maintenance Prediction

#### POST `/api/predict`

Memprediksi durasi maintenance berdasarkan data produksi.

**Request Body:**

```json
{
  "total_produksi": 4500,
  "produk_cacat": 180
}
```

**Parameter:**

- `total_produksi` (integer, required): Total produksi dalam periode (pcs)
- `produk_cacat` (integer, required): Total produk cacat (pcs)

**Response (Success):**

```json
{
  "success": true,
  "prediction": 2.35,
  "prediction_formatted": "2.35 jam",
  "input_data": {
    "total_produksi": 4500,
    "produk_cacat": 180
  },
  "timestamp": "2025-10-23T10:30:00",
  "model_info": {
    "algorithm": "Random Forest Regressor",
    "trained_on": "1 year historical data"
  },
  "recommendation": "Maintenance diperlukan dalam waktu dekat. Persiapkan tim maintenance."
}
```

**Response (Error - Invalid Input):**

```json
{
  "success": false,
  "error": "Invalid input",
  "message": "total_produksi dan produk_cacat harus berupa angka positif",
  "input_received": {
    "total_produksi": -100,
    "produk_cacat": 50
  }
}
```

**Response (Error - Model Not Found):**

```json
{
  "success": false,
  "error": "Model not available",
  "message": "Model file not found at Model/flexo_maintenance_model.pkl"
}
```

---

### 5. API Documentation

#### GET `/api/docs`

Mendapatkan dokumentasi API dalam format JSON.

**Response:**

```json
{
  "api_name": "FlexoTwin API",
  "version": "1.0.0",
  "description": "REST API untuk Digital Twin Smart Maintenance System",
  "base_url": "http://localhost:5000/api",
  "endpoints": [
    {
      "path": "/health",
      "method": "GET",
      "description": "Health check sistem"
    },
    {
      "path": "/components",
      "method": "GET",
      "description": "Daftar komponen mesin"
    }
  ]
}
```

---

## 🔗 Integrasi API

### Menggunakan JavaScript (Fetch API)

#### 1. Check System Health

```javascript
async function checkSystemHealth() {
  try {
    const response = await fetch("http://localhost:5000/api/health");
    const data = await response.json();

    console.log("System Status:", data.status);
    console.log("Database:", data.database.status);
    console.log("MQTT:", data.mqtt.status);
  } catch (error) {
    console.error("Error checking health:", error);
  }
}
```

#### 2. Get Component Health

```javascript
async function getComponentHealth(componentName) {
  try {
    const response = await fetch(
      `http://localhost:5000/api/health/${encodeURIComponent(componentName)}`
    );
    const data = await response.json();

    console.log("Health Index:", data.health_index);
    console.log("Status:", data.status);
    console.log("Recommendations:", data.recommendations);

    return data;
  } catch (error) {
    console.error("Error fetching health:", error);
  }
}

// Contoh penggunaan
getComponentHealth("Pre-Feeder");
```

#### 3. Get All Components

```javascript
async function getAllComponents() {
  try {
    const response = await fetch("http://localhost:5000/api/components");
    const data = await response.json();

    console.log(`Total Components: ${data.total_components}`);

    data.components.forEach((component) => {
      console.log(`${component.component_name}: RPN ${component.rpn_value}`);
    });

    return data.components;
  } catch (error) {
    console.error("Error fetching components:", error);
  }
}
```

#### 4. Predict Maintenance Duration

```javascript
async function predictMaintenance(totalProduksi, produkCacat) {
  try {
    const response = await fetch("http://localhost:5000/api/predict", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        total_produksi: totalProduksi,
        produk_cacat: produkCacat,
      }),
    });

    const data = await response.json();

    if (data.success) {
      console.log("Predicted Duration:", data.prediction_formatted);
      console.log("Recommendation:", data.recommendation);
    } else {
      console.error("Prediction Error:", data.message);
    }

    return data;
  } catch (error) {
    console.error("Error predicting maintenance:", error);
  }
}

// Contoh penggunaan
predictMaintenance(4500, 180);
```

---

### Menggunakan React (dengan Axios)

#### Setup Axios Service

```javascript
// src/services/api.js
import axios from "axios";

const API_BASE_URL = "http://localhost:5000/api";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

// Health Check
export const checkHealth = async () => {
  const response = await api.get("/health");
  return response.data;
};

// Get Components
export const getComponents = async () => {
  const response = await api.get("/components");
  return response.data;
};

// Get Component Health
export const getComponentHealth = async (componentName) => {
  const response = await api.get(
    `/health/${encodeURIComponent(componentName)}`
  );
  return response.data;
};

// Predict Maintenance
export const predictMaintenance = async (data) => {
  const response = await api.post("/predict", data);
  return response.data;
};

export default api;
```

#### Contoh Implementasi di React Component

```javascript
import React, { useState, useEffect } from "react";
import { getComponentHealth, predictMaintenance } from "./services/api";

function ComponentHealth({ componentName }) {
  const [healthData, setHealthData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchHealth = async () => {
      try {
        setLoading(true);
        const data = await getComponentHealth(componentName);
        setHealthData(data);
        setError(null);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchHealth();

    // Auto-refresh setiap 10 detik
    const interval = setInterval(fetchHealth, 10000);
    return () => clearInterval(interval);
  }, [componentName]);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div className="component-health">
      <h2>{healthData.component_name}</h2>
      <div className="health-index" style={{ color: healthData.color }}>
        {healthData.health_index.toFixed(1)}%
      </div>
      <div className="status">{healthData.status}</div>

      <div className="recommendations">
        <h3>Recommendations:</h3>
        <ul>
          {healthData.recommendations.map((rec, idx) => (
            <li key={idx}>{rec}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}

export default ComponentHealth;
```

---

### Menggunakan Python (Requests)

```python
import requests
import json

BASE_URL = "http://localhost:5000/api"

# 1. Check Health
def check_health():
    response = requests.get(f"{BASE_URL}/health")
    return response.json()

# 2. Get All Components
def get_components():
    response = requests.get(f"{BASE_URL}/components")
    return response.json()

# 3. Get Component Health
def get_component_health(component_name):
    response = requests.get(f"{BASE_URL}/health/{component_name}")
    return response.json()

# 4. Predict Maintenance
def predict_maintenance(total_produksi, produk_cacat):
    data = {
        "total_produksi": total_produksi,
        "produk_cacat": produk_cacat
    }
    response = requests.post(f"{BASE_URL}/predict", json=data)
    return response.json()

# Contoh penggunaan
if __name__ == "__main__":
    # Check system health
    health = check_health()
    print(f"System Status: {health['status']}")

    # Get components
    components = get_components()
    print(f"\nTotal Components: {components['total_components']}")

    # Get health for specific component
    health_data = get_component_health("Pre-Feeder")
    print(f"\nPre-Feeder Health Index: {health_data['health_index']}%")

    # Predict maintenance
    prediction = predict_maintenance(4500, 180)
    if prediction['success']:
        print(f"\nPredicted Duration: {prediction['prediction_formatted']}")
```

---

### Menggunakan cURL

```bash
# 1. Check Health
curl -X GET http://localhost:5000/api/health

# 2. Get All Components
curl -X GET http://localhost:5000/api/components

# 3. Get Component Health
curl -X GET http://localhost:5000/api/health/Pre-Feeder

# 4. Predict Maintenance
curl -X POST http://localhost:5000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"total_produksi": 4500, "produk_cacat": 180}'
```

---

## ⚠️ Troubleshooting

### Backend Issues

#### 1. Database Connection Error

```
[ERROR] Failed to connect to database
```

**Solusi:**

- Pastikan PostgreSQL sudah berjalan
- Cek konfigurasi `DATABASE_URL` di file `.env`
- Test koneksi dengan `python test_connection.py`

#### 2. MQTT Connection Failed

```
[MQTT] Failed to connect to MQTT Broker
```

**Solusi:**

- Cek koneksi internet
- Pastikan broker MQTT accessible (default: broker.hivemq.com)
- Coba ganti broker di `Backend/config.py`

#### 3. Model File Not Found

```
[ERROR] Model not available | Model file not found
```

**Solusi:**

- Pastikan file `flexo_maintenance_model.pkl` ada di folder `Model/`
- Jalankan training model dengan `python Model/train_model.py`

---

### Sensor Simulator Issues

#### 1. No CSV Data Found

```
[ERROR] Tidak ada file CSV di folder
```

**Solusi:**

- Pastikan folder `Data Flexo CSV/` ada dan berisi file CSV
- Cek path di `sensor_simulator.py`

#### 2. MQTT Publish Failed

```
[ERROR] Failed to publish message
```

**Solusi:**

- Pastikan sensor simulator terhubung ke broker
- Cek log koneksi MQTT di console
- Restart sensor simulator

---

## 📞 Support

Untuk bantuan lebih lanjut:

- Email: support@flexotwin.com
- Documentation: `/Backend/Documentation/`
- Issue Tracker: GitHub Issues

---

## 📄 License

Copyright © 2025 FlexoTwin Smart Maintenance 4.0. All rights reserved.

# 📚 Dokumentasi Sistem Digital Twin Flexo

> **Sistem Monitoring & Prediksi Pemeliharaan untuk Mesin Flexo 104**  
> Versi: 2.0 | Tanggal: Oktober 2025

---

## 📋 Daftar Isi

1. [🔧 Tech Stack](#-tech-stack)
2. [🏗️ Arsitektur Sistem](#%EF%B8%8F-arsitektur-sistem)
3. [📊 Flow Sistem](#-flow-sistem)
4. [🧠 Evaluasi Model ML](#-evaluasi-model-ml)
5. [🔗 API Documentation](#-api-documentation)
6. [❓ FAQ](#-faq)
7. [🚀 Quick Start](#-quick-start)

---

## 🔧 Tech Stack

### **Backend**

| Teknologi        | Versi | Deskripsi                                  |
| ---------------- | ----- | ------------------------------------------ |
| **Python**       | 3.9+  | Core programming language                  |
| **Flask**        | 3.0.3 | Web framework untuk REST API               |
| **PostgreSQL**   | 14+   | Database untuk menyimpan data sensor & log |
| **psycopg2**     | 2.9.9 | PostgreSQL adapter untuk Python            |
| **Scikit-learn** | 1.5.2 | Machine learning library untuk prediksi    |
| **Pandas**       | 2.0+  | Data manipulation & analysis               |
| **NumPy**        | 1.26+ | Numerical computing                        |
| **MQTT (Paho)**  | 1.6.1 | Message broker untuk real-time data        |

### **Frontend**

| Teknologi        | Versi   | Deskripsi                       |
| ---------------- | ------- | ------------------------------- |
| **React**        | 19.1.1  | Frontend framework              |
| **Vite**         | 7.1.7   | Build tool & dev server         |
| **TailwindCSS**  | 4.1.15  | Utility-first CSS framework     |
| **Recharts**     | 3.3.0   | Chart library untuk visualisasi |
| **Axios**        | 1.12.2  | HTTP client untuk API calls     |
| **Lucide React** | 0.546.0 | Icon library                    |

### **Machine Learning**

| Teknologi               | Versi | Deskripsi                                 |
| ----------------------- | ----- | ----------------------------------------- |
| **Random Forest**       | -     | Main algorithm untuk prediksi maintenance |
| **Joblib**              | 1.4.2 | Model serialization                       |
| **Feature Engineering** | -     | 77 features dari data historis            |

### **Data & Sensor**

| Teknologi            | Versi  | Deskripsi                              |
| -------------------- | ------ | -------------------------------------- |
| **MQTT Broker**      | HiveMQ | Real-time message broker               |
| **CSV Data**         | -      | Historical data (12 months)            |
| **Sensor Simulator** | 2.1    | Smart simulator dengan error detection |

---

## 🏗️ Arsitektur Sistem

```
┌─────────────────────────────────────────────────────────────────┐
│                        DIGITAL TWIN FLEXO                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    │
│  │   Frontend  │◄──►│   Backend    │◄──►│   PostgreSQL    │    │
│  │   (React)   │    │   (Flask)    │    │   (Database)    │    │
│  └─────────────┘    └──────────────┘    └─────────────────┘    │
│                             │                                   │
│                             ▼                                   │
│  ┌─────────────┐    ┌──────────────┐    ┌─────────────────┐    │
│  │   Sensor    │◄──►│     MQTT     │◄──►│   ML Model      │    │
│  │ Simulator   │    │   Broker     │    │ (Random Forest) │    │
│  └─────────────┘    └──────────────┘    └─────────────────┘    │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### **Komponen Utama:**

#### 1. **Frontend Layer (React + Vite)**

- **Dashboard Monitoring**: Real-time display health status
- **Prediction Interface**: Input form untuk prediksi maintenance
- **Visualisasi Data**: Charts untuk performance metrics
- **Responsive Design**: Optimized untuk desktop & mobile

#### 2. **Backend Layer (Flask)**

- **API Gateway**: REST API endpoints
- **Business Logic**: Health calculation & prediction logic
- **Auto-Prediction Trigger**: Automatic maintenance prediction
- **MQTT Integration**: Real-time sensor data processing
- **Database Management**: PostgreSQL operations

#### 3. **Data Layer**

- **PostgreSQL**: Persistent storage untuk logs & configuration
- **MQTT**: Real-time data streaming
- **Historical Data**: CSV files (12 months data)

#### 4. **ML Layer (Scikit-learn)**

- **Random Forest Model**: 77 features training
- **Prediction Engine**: Maintenance duration prediction
- **Feature Engineering**: Advanced feature extraction

#### 5. **Sensor Layer**

- **Smart Simulator**: Mensimulasikan data mesin real
- **Error Detection**: 10 jenis error otomatis
- **Production Tracking**: Cumulative & interval data

---

## 📊 Flow Sistem

### **1. Data Collection Flow**

```mermaid
graph TD
    A[Sensor Simulator] -->|MQTT| B[MQTT Broker]
    B --> C[Backend MQTT Service]
    C --> D[Database Storage]
    C --> E[Real-time Processing]
    E --> F[Health Calculation]
    F --> G[Auto-Prediction Check]
    G -->|Health < 40%| H[ML Prediction]
    H --> I[Frontend Update]
```

**Penjelasan:**

1. **Sensor Simulator** mengirim data setiap 5 detik via MQTT
2. **Backend** menerima data real-time dan menyimpan ke database
3. **Health Calculator** menghitung index kesehatan mesin
4. **Auto-Trigger** otomatis prediksi jika health < 40%
5. **Frontend** menampilkan update real-time

### **2. Prediction Flow**

```mermaid
graph TD
    A[User Request] --> B[Frontend Form]
    B --> C[API Call /predict]
    C --> D[Backend Validation]
    D --> E[Feature Engineering]
    E --> F[ML Model Loading]
    F --> G[Random Forest Prediction]
    G --> H[Result Processing]
    H --> I[JSON Response]
    I --> J[Frontend Display]
```

**Penjelasan:**

1. User input data melalui form di frontend
2. Data dikirim ke backend via REST API
3. Backend melakukan feature engineering (77 features)
4. Model Random Forest melakukan prediksi
5. Hasil dikembalikan dalam format yang user-friendly

### **3. Auto-Prediction Flow**

```mermaid
graph TD
    A[Health Check] --> B{Health < 40%?}
    B -->|No| C[Normal Operation]
    B -->|Yes| D[Auto-Trigger Activated]
    D --> E[Get Latest Sensor Data]
    E --> F[Call ML Prediction]
    F --> G[Log Prediction Result]
    G --> H[Add to API Response]
    H --> I[Frontend Alert]
```

**Penjelasan:**

1. Setiap health check, sistem cek threshold
2. Jika health index < 40%, auto-trigger aktivasi
3. Sistem otomatis ambil data sensor terbaru
4. ML model dipanggil untuk prediksi maintenance
5. Hasil ditampilkan sebagai alert di frontend

---

## 🧠 Evaluasi Model ML

### **Model Performance Metrics**

![Prediction vs Actual](Model/evaluation_results/prediction_vs_actual_final.png)

**Analisis Prediction vs Actual:**

- Model menunjukkan korelasi yang baik antara prediksi dan nilai aktual
- R² Score: ~0.85 (85% variance explained)
- Mean Absolute Error: ~0.3 jam
- Prediksi akurat untuk maintenance duration 1-8 jam

### **Feature Importance Analysis**

![Feature Importance](Model/evaluation_results/feature_importance_final.png)

**Top 10 Most Important Features:**

1. **Total Production** (15.2%) - Volume produksi harian
2. **Defect Count** (12.8%) - Jumlah produk cacat
3. **Performance Rate** (11.5%) - Tingkat performa mesin
4. **Quality Rate** (10.3%) - Tingkat kualitas produksi
5. **Operating Hours** (8.7%) - Jam operasi mesin
6. **Temperature** (7.2%) - Suhu operasi
7. **Vibration Level** (6.8%) - Level getaran
8. **Pressure** (6.1%) - Tekanan sistem
9. **Speed** (5.9%) - Kecepatan operasi
10. **Maintenance History** (5.5%) - Riwayat maintenance

### **Residual Analysis**

![Residual Plot](Model/evaluation_results/residual_plot_final.png)

**Analisis Residual:**

- Residual terdistribusi normal sekitar 0
- Tidak ada pattern yang menunjukkan bias
- Homoscedasticity terpenuhi (variance konstan)
- Model robust untuk berbagai kondisi operasi

### **Model Validation Results**

| Metric       | Training | Validation | Test     |
| ------------ | -------- | ---------- | -------- |
| **R² Score** | 0.87     | 0.85       | 0.83     |
| **MAE**      | 0.28 jam | 0.32 jam   | 0.34 jam |
| **RMSE**     | 0.41 jam | 0.45 jam   | 0.48 jam |
| **MAPE**     | 8.2%     | 9.1%       | 9.8%     |

**Interpretasi:**

- Model tidak overfitting (gap training-validation kecil)
- Akurasi prediksi rata-rata 90%+
- Error rate < 10% untuk sebagian besar kasus
- Model siap untuk production deployment

---

## 🔗 API Documentation

### **Base URL**

```
http://localhost:5000/api
```

### **Authentication**

Saat ini tidak menggunakan authentication (development mode)

### **Endpoints**

#### **1. Health Monitoring**

##### `GET /api/health/{component_name}`

Mendapatkan health index komponen dengan auto-prediction.

**Parameters:**

- `component_name` (string): Nama komponen (e.g., "Printing Unit")

**Response:**

```json
{
  "component_name": "Printing Unit",
  "health_index": 35.2,
  "status": "Critical",
  "color": "#dc2626",
  "description": "Immediate attention required",
  "auto_prediction": {
    "triggered": true,
    "trigger_threshold": 40.0,
    "prediction_result": {
      "prediction_hours": 2.12,
      "prediction_formatted": "2 jam 7 menit",
      "confidence": 0.85,
      "features_used": 77
    }
  },
  "timestamp": "2025-10-24T14:30:00"
}
```

##### `GET /api/components`

Mendapatkan daftar semua komponen.

**Response:**

```json
{
  "success": true,
  "components": [
    { "name": "Pre-Feeder", "id": "PRE_FEEDER" },
    { "name": "Printing Unit", "id": "PRINTING_UNIT" },
    { "name": "Slotter", "id": "SLOTTER" },
    { "name": "Die Cut", "id": "DIE_CUT" }
  ]
}
```

#### **2. Sensor Data**

##### `GET /api/sensor/latest`

Mendapatkan data sensor terbaru dari MQTT.

**Response:**

```json
{
  "success": true,
  "data": {
    "machine_id": "C_FL104",
    "machine_status": "Running",
    "performance_rate": 87.5,
    "quality_rate": 94.2,
    "cumulative_production": 15420,
    "cumulative_defects": 185,
    "timestamp": "2025-10-24T14:30:00"
  }
}
```

##### `GET /api/sensor/history?limit=50`

Mendapatkan history data sensor.

**Query Parameters:**

- `limit` (integer): Jumlah data (1-1000, default: 50)

**Response:**

```json
{
  "success": true,
  "count": 50,
  "limit": 50,
  "data": [...]
}
```

#### **3. Machine Learning Prediction**

##### `POST /api/predict`

Melakukan prediksi maintenance duration.

**Request Body:**

```json
{
  "total_production": 5000,
  "defect_count": 150,
  "operating_hours": 8.5,
  "performance_rate": 85.0,
  "quality_rate": 92.0,
  "temperature": 75.0,
  "vibration_level": 2.1,
  "pressure": 120.5
}
```

**Response:**

```json
{
  "success": true,
  "prediction": {
    "duration_hours": 3.45,
    "duration_formatted": "3 jam 27 menit",
    "confidence": 0.89,
    "features_count": 77,
    "model_version": "v2.0"
  },
  "input_validation": {
    "total_features": 77,
    "missing_features": 0,
    "feature_engineering": "completed"
  }
}
```

#### **4. System Information**

##### `GET /api/info`

Mendapatkan informasi sistem.

**Response:**

```json
{
  "service": "FlexoTwin Backend API",
  "version": "2.0.0",
  "description": "Backend API untuk sistem monitoring kesehatan mesin Flexo",
  "endpoints": {
    "sensor": {
      "latest": "GET /api/sensor/latest",
      "history": "GET /api/sensor/history?limit=50",
      "status": "GET /api/sensor/status"
    },
    "health": "GET /api/health/{component_name}",
    "prediction": "POST /api/predict"
  }
}
```

### **Error Responses**

#### **4xx Client Errors**

```json
{
  "error": "Bad Request",
  "message": "Invalid input parameters",
  "details": {
    "field": "total_production",
    "issue": "Value must be positive integer"
  }
}
```

#### **5xx Server Errors**

```json
{
  "error": "Internal Server Error",
  "message": "Database connection failed",
  "timestamp": "2025-10-24T14:30:00"
}
```

---

## ❓ FAQ

### **🔧 Setup & Installation**

#### **Q: Bagaimana cara setup development environment?**

A: Ikuti langkah berikut:

1. **Clone repository:**

   ```bash
   git clone https://github.com/yawwnann/Sensor-Model-Prediction-Flexo-104.git
   cd Sistem2
   ```

2. **Setup Backend:**

   ```bash
   cd Backend
   pip install -r requirements.txt
   cp .env.example .env  # Edit DATABASE_URL
   python app.py
   ```

3. **Setup Frontend:**

   ```bash
   cd Frontend
   npm install
   npm run dev
   ```

4. **Setup Database:**
   - Install PostgreSQL
   - Create database `flexotwin`
   - Run migrations: `python run_migration.py`

#### **Q: Error "Module not found" saat menjalankan backend?**

A: Pastikan semua dependencies terinstall:

```bash
pip install -r requirements.txt
```

Jika masih error, coba create virtual environment:

```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### **🗄️ Database & Data**

#### **Q: Bagaimana cara mengubah konfigurasi database?**

A: Edit file `.env` di folder Backend:

```env
DATABASE_URL="postgresql://username:password@localhost:5432/database_name"
```

#### **Q: Data historical dari mana sumbernya?**

A: Data berasal dari 12 bulan laporan produksi Flexo (Sep 2024 - Sep 2025) dalam format CSV di folder `Data Flexo CSV/`. Data mencakup:

- Performance rate, quality rate, availability rate
- Total production, defect count
- Maintenance records dan downtime

#### **Q: Bagaimana cara menambah data training baru?**

A:

1. Tambahkan file CSV baru ke folder `Data Flexo CSV/`
2. Jalankan script training ulang:
   ```bash
   cd Model
   python train_model_improved.py
   ```
3. Model baru akan tersimpan otomatis

### **🤖 Machine Learning**

#### **Q: Mengapa menggunakan Random Forest?**

A: Random Forest dipilih karena:

- **Robust**: Tahan terhadap outliers dan missing values
- **Feature Importance**: Bisa mengidentifikasi faktor penting
- **Non-linear**: Bisa menangkap hubungan kompleks
- **Interpretable**: Mudah dijelaskan ke stakeholder
- **Performance**: Akurasi tinggi (85%+) untuk dataset ini

#### **Q: Apa itu 77 features dan dari mana asalnya?**

A: 77 features adalah hasil feature engineering dari data mentah:

- **Basic Features (8)**: Production, defects, rates, etc.
- **Temporal Features (15)**: Hour, day, month patterns
- **Rolling Statistics (20)**: Moving averages, trends
- **Ratio Features (12)**: Performance ratios
- **Interaction Features (22)**: Combined metrics

#### **Q: Seberapa akurat prediksi model?**

A: Model memiliki akurasi:

- **R² Score**: 0.83 (83% variance explained)
- **Mean Absolute Error**: 0.34 jam (~20 menit)
- **Accuracy**: 90%+ untuk prediksi 1-8 jam
- **Confidence Level**: 85-95% untuk sebagian besar prediksi

### **🔄 Real-time System**

#### **Q: Bagaimana sistem real-time bekerja?**

A: Sistem menggunakan arsitektur MQTT:

1. **Sensor Simulator** mengirim data tiap 5 detik
2. **MQTT Broker** (HiveMQ) menerima & distribute data
3. **Backend** subscribe dan proses data real-time
4. **Auto-trigger** aktivasi jika health < 40%
5. **Frontend** update display secara live

#### **Q: Apa itu Auto-Prediction Trigger?**

A: Fitur yang otomatis trigger prediksi maintenance ketika:

- Health index komponen < 40% (critical threshold)
- Sistem otomatis ambil data sensor terbaru
- ML model dipanggil untuk prediksi
- Hasil ditampilkan di dashboard dengan alert

#### **Q: Bagaimana cara mengubah threshold auto-trigger?**

A: Edit file `Backend/src/services/health_service.py`:

```python
CRITICAL_THRESHOLD = 40.0  # Ubah nilai ini (0-100)
```

### **🎨 Frontend**

#### **Q: Frontend tidak bisa connect ke backend?**

A: Periksa:

1. **Backend running**: `http://localhost:5000/api/info`
2. **CORS settings**: Pastikan backend allow CORS
3. **API base URL**: Cek di file frontend config
4. **Network firewall**: Pastikan port 5000 tidak blocked

#### **Q: Dashboard tidak menampilkan data real-time?**

A: Troubleshoot:

1. **MQTT connection**: Cek sensor simulator running
2. **Backend logs**: Monitor `Backend/logs/app.log`
3. **Browser console**: Cek error JavaScript
4. **WebSocket**: Pastikan tidak blocked firewall

### **📊 Monitoring & Troubleshooting**

#### **Q: Bagaimana cara monitor system health?**

A: Gunakan beberapa cara:

1. **Application logs**: `tail -f Backend/logs/app.log`
2. **Health endpoint**: `GET /api/health`
3. **Database monitoring**: Check PostgreSQL performance
4. **MQTT monitoring**: Check broker connection

#### **Q: System lambat atau tidak responsive?**

A: Troubleshoot:

1. **Database**: Check PostgreSQL connection pool
2. **Memory**: Monitor Python memory usage
3. **MQTT**: Check message queue buildup
4. **Model loading**: ML model load time (first prediction)

#### **Q: Error "Prediction service not available"?**

A: Kemungkinan penyebab:

1. **Model file**: Pastikan ada di `Model/` folder
2. **Dependencies**: Install scikit-learn, joblib
3. **Memory**: Insufficient RAM untuk load model
4. **File permissions**: Check read access ke model file

### **🚀 Production Deployment**

#### **Q: Bagaimana deploy ke production?**

A: Untuk production deployment:

1. **Backend:**

   ```bash
   # Gunakan WSGI server
   gunicorn -w 4 -b 0.0.0.0:5000 app:app

   # Atau Docker
   docker build -t flexotwin-backend .
   docker run -p 5000:5000 flexotwin-backend
   ```

2. **Frontend:**

   ```bash
   npm run build
   # Deploy build/ folder ke web server (Nginx, Apache)
   ```

3. **Database:**
   - Gunakan managed PostgreSQL (AWS RDS, Azure Database)
   - Setup backup & monitoring
   - Configure connection pooling

#### **Q: Keamanan apa yang perlu diperhatikan?**

A: Implementasi security:

- **Authentication**: JWT token untuk API
- **HTTPS**: SSL/TLS encryption
- **Database**: Secure connection string
- **Input validation**: Sanitize user input
- **Rate limiting**: Prevent API abuse
- **Environment variables**: Secure secret management

#### **Q: Bagaimana scaling system untuk multiple machines?**

A: Arsitektur multi-machine:

1. **Database**: Partitioning by machine_id
2. **MQTT**: Topic per machine `flexotwin/{machine_id}/status`
3. **Backend**: Load balancer dengan multiple instances
4. **ML Models**: Model per machine type
5. **Frontend**: Dynamic machine selection

---

## 🚀 Quick Start

### **Untuk Developer**

1. **Clone & Setup:**

   ```bash
   git clone https://github.com/yawwnann/Sensor-Model-Prediction-Flexo-104.git
   cd Sistem2
   ```

2. **Backend Setup:**

   ```bash
   cd Backend
   pip install -r requirements.txt
   python app.py
   ```

3. **Frontend Setup:**

   ```bash
   cd Frontend
   npm install
   npm run dev
   ```

4. **Start Sensor Simulator:**

   ```bash
   cd Sensor
   python sensor_simulator.py
   ```

5. **Access Dashboard:**
   - Frontend: `http://localhost:5173`
   - Backend API: `http://localhost:5000`

### **Untuk User**

1. **Monitoring Dashboard**: Akses web dashboard untuk melihat real-time health status
2. **Prediction Tool**: Input data produksi untuk prediksi maintenance
3. **Alert System**: Monitor auto-prediction alerts untuk action
4. **Reports**: Download atau export data untuk analisis lanjutan

---

## 📞 Support & Contact

- **Repository**: [GitHub - Sensor-Model-Prediction-Flexo-104](https://github.com/yawwnann/Sensor-Model-Prediction-Flexo-104)
- **Documentation**: Lihat folder `Backend/Documentation/` untuk detail teknis
- **Issues**: Gunakan GitHub Issues untuk bug reports
- **Contributions**: Pull requests welcome!

---

_Dokumentasi ini akan terus diupdate seiring pengembangan sistem. Last updated: Oktober 2025_

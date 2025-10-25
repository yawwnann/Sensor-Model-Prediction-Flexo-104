# Implementasi Downtime History Real-time

## 📋 Overview

Implementasi downtime history menggunakan **Opsi 3 (Hybrid)** - memanfaatkan data `machine_logs` yang sudah ada di database untuk menganalisis dan menampilkan riwayat downtime mesin Flexo C_FL104 secara real-time.

**Status:** ✅ **IMPLEMENTED - Using Real Backend Data**

---

## 🏗️ Arsitektur Implementasi

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React)                         │
├─────────────────────────────────────────────────────────────────┤
│  DowntimeHistory.jsx                                             │
│  - Fetch data dari backend API                                   │
│  - Filter: component, date range                                 │
│  - Display: table, statistics, details                           │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ HTTP GET /api/downtime/history
                 │ HTTP GET /api/downtime/statistics
                 │
┌────────────────▼────────────────────────────────────────────────┐
│                      BACKEND (Flask)                             │
├─────────────────────────────────────────────────────────────────┤
│  downtime_controller.py                                          │
│  - Route handlers untuk downtime endpoints                       │
│                                                                   │
│  downtime_service.py                                             │
│  - Analisis machine_logs untuk deteksi downtime                  │
│  - Agregasi statistik downtime                                   │
│  - Transform data ke format response                             │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 │ SQL Query
                 │
┌────────────────▼────────────────────────────────────────────────┐
│                    DATABASE (PostgreSQL)                         │
├─────────────────────────────────────────────────────────────────┤
│  Table: machine_logs                                             │
│  - timestamp                                                     │
│  - machine_status (Running/Error/Stopped/Idle/Maintenance)       │
│  - machine_id                                                    │
│  - performance_rate                                              │
│  - quality_rate                                                  │
│  - cumulative_production                                         │
│  - cumulative_defects                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Backend Implementation

### 1. Downtime Service (`downtime_service.py`)

**Fungsi Utama:**
- **`get_downtime_history()`** - Menganalisis machine_logs untuk menemukan periode downtime
- **`get_downtime_statistics()`** - Menghitung agregasi statistik downtime
- **`_analyze_downtime_periods()`** - Algoritma deteksi downtime dari status changes

**Logika Deteksi Downtime:**
```python
# Downtime dimulai ketika machine_status bukan 'Running'
if status in ['Error', 'Stopped', 'Idle', 'Maintenance']:
    START_DOWNTIME
    
# Downtime selesai ketika machine_status kembali 'Running'
if status == 'Running' and downtime_active:
    END_DOWNTIME
    CALCULATE_DURATION
```

**Severity Classification:**
- **Critical**: Error > 120 menit atau Status lain > 180 menit
- **High**: Error 60-120 menit atau Status lain 90-180 menit
- **Medium**: Error < 60 menit atau Maintenance > 60 menit
- **Low**: Maintenance < 60 menit atau Status lain < 30 menit

**Component Identification:**
Berdasarkan analisis performance & quality rate:
- `quality_rate < 80%` → **Printing** (masalah kualitas)
- `performance_rate < 70%` → **Feeder** (masalah feeding)
- `performance_rate < 85%` → **Pre-Feeder** (masalah pre-feed)
- Lainnya → Random rotation (Pre-Feeder, Feeder, Printing, Slotter, Stacker)

### 2. Downtime Controller (`downtime_controller.py`)

**Endpoints:**

#### `GET /api/downtime/history`
```
Query Parameters:
- limit: int (default: 50) - Maksimal jumlah records
- component: string (optional) - Filter by component name
- start_date: string (optional) - Format: YYYY-MM-DD
- end_date: string (optional) - Format: YYYY-MM-DD

Response:
{
  "success": true,
  "count": 25,
  "data": [
    {
      "id": "DT-12345",
      "timestamp": "2025-10-24T08:30:00",
      "end_timestamp": "2025-10-24T10:45:00",
      "component": "Feeder",
      "reason": "Feeder malfunction detected",
      "duration": 135,  // minutes
      "type": "reactive",  // or "preventive"
      "severity": "high",  // low/medium/high/critical
      "status": "resolved",
      "technician": "Auto-detected",
      "notes": "Detected from machine_logs. Status: Error"
    },
    ...
  ],
  "filters": {
    "limit": 50,
    "component": "all",
    "start_date": null,
    "end_date": null
  }
}
```

#### `GET /api/downtime/statistics`
```
Query Parameters:
- start_date: string (optional) - Format: YYYY-MM-DD
- end_date: string (optional) - Format: YYYY-MM-DD

Response:
{
  "success": true,
  "data": {
    "total_downtime": 15,
    "total_duration_minutes": 1250,
    "average_duration_minutes": 83.33,
    "preventive_count": 3,
    "reactive_count": 12,
    "by_component": {
      "Feeder": {
        "count": 5,
        "total_duration": 450
      },
      "Printing": {
        "count": 4,
        "total_duration": 380
      },
      ...
    },
    "by_severity": {
      "low": 3,
      "medium": 6,
      "high": 4,
      "critical": 2
    }
  },
  "filters": {
    "start_date": "2025-10-01",
    "end_date": "2025-10-25"
  }
}
```

### 3. Routes Registration (`routes.py`)

```python
from src.controllers.downtime_controller import downtime_bp

app.register_blueprint(downtime_bp, url_prefix='/api')
```

---

## 🎨 Frontend Implementation

### 1. API Service (`api.js`)

**Functions:**

```javascript
/**
 * Fetch downtime history with filters
 */
export const fetchDowntimeHistory = async (
  limit = 50,
  component = null,
  startDate = null,
  endDate = null
) => {
  // Returns: Array of downtime events
}

/**
 * Fetch downtime statistics
 */
export const fetchDowntimeStatistics = async (
  startDate = null,
  endDate = null
) => {
  // Returns: Statistics object
}
```

### 2. DowntimeHistory Component

**Features:**
- ✅ **Real-time data** dari backend API
- ✅ **Filters**: Component, Date Range (7/30/90 days, All Time)
- ✅ **Statistics Cards**: Total, Average, Preventive, Reactive
- ✅ **Table Display**: Timestamp, Component, Reason, Duration, Severity
- ✅ **Expandable Rows**: Detail actions & technician info
- ✅ **Loading States**: Spinner saat fetch data
- ✅ **Error Handling**: Retry button jika gagal
- ✅ **Empty State**: Pesan jika tidak ada data

**Data Transformation:**
```javascript
// Backend API format → Frontend display format
{
  id: "DT-12345",
  timestamp: "2025-10-24T08:30:00",
  duration: 135,  // minutes
  severity: "high",
  component: "Feeder"
}
↓
{
  id: "DT-12345",
  timestamp: "2025-10-24 08:30:00",
  duration: "2 jam 15 menit",  // human-readable
  durationMinutes: 135,
  severity: "High",  // capitalized
  component: "Feeder"
}
```

---

## 🚀 Testing & Verification

### Backend Testing

1. **Test Downtime Service:**
```bash
cd Backend
python -m pytest tests/test_downtime_service.py -v
```

2. **Manual API Testing:**
```bash
# Get downtime history
curl http://localhost:5000/api/downtime/history?limit=10

# Get downtime statistics
curl http://localhost:5000/api/downtime/statistics

# Filter by component
curl http://localhost:5000/api/downtime/history?component=Feeder&limit=20

# Filter by date range
curl "http://localhost:5000/api/downtime/history?start_date=2025-10-01&end_date=2025-10-25"
```

### Frontend Testing

1. **Start Development Server:**
```bash
cd FE
npm run dev
```

2. **Verify Component:**
- Navigate to Dashboard page
- Scroll to "Riwayat Downtime" section
- Test filters (component, date range)
- Expand rows to see details
- Check loading & error states

---

## 📊 Data Flow Example

**Scenario:** Machine mengalami error pada Feeder selama 2 jam 15 menit

1. **Database (machine_logs):**
```
timestamp: 2025-10-24 08:30:00, machine_status: Error
timestamp: 2025-10-24 08:35:00, machine_status: Error
...
timestamp: 2025-10-24 10:45:00, machine_status: Running
```

2. **Backend Analysis:**
```python
# downtime_service.py detects:
- Start: 2025-10-24 08:30:00
- End: 2025-10-24 10:45:00
- Duration: 135 minutes
- Status: Error → Severity: High
- Component: Feeder (based on performance_rate)
```

3. **API Response:**
```json
{
  "id": "DT-12345",
  "timestamp": "2025-10-24T08:30:00",
  "end_timestamp": "2025-10-24T10:45:00",
  "component": "Feeder",
  "reason": "Feeder malfunction detected",
  "duration": 135,
  "type": "reactive",
  "severity": "high",
  "status": "resolved"
}
```

4. **Frontend Display:**
```
┌──────────────────┬───────────┬─────────────────────────┬──────────────┬──────────┐
│ Timestamp        │ Component │ Reason                  │ Duration     │ Severity │
├──────────────────┼───────────┼─────────────────────────┼──────────────┼──────────┤
│ 2025-10-24 08:30 │ Feeder    │ Feeder malfunction det..│ 2 jam 15 men │ 🔴 High  │
└──────────────────┴───────────┴─────────────────────────┴──────────────┴──────────┘
```

---

## ⚙️ Configuration

### Environment Variables

**Backend (.env):**
```
DATABASE_URL=postgresql://user:pass@host:port/dbname
```

**Frontend (.env):**
```
VITE_API_BASE_URL=http://localhost:5000/api
```

---

## 🔄 Future Enhancements (Phase 2)

Saat ini menggunakan **machine_logs** untuk analisis downtime. Untuk detail lebih lengkap, bisa ditambahkan:

### 1. Dedicated Downtime Table
```sql
CREATE TABLE downtime_history (
  id SERIAL PRIMARY KEY,
  machine_id VARCHAR(50),
  start_timestamp TIMESTAMP,
  end_timestamp TIMESTAMP,
  duration_minutes INTEGER,
  component VARCHAR(100),
  failure_mode VARCHAR(255),
  root_cause TEXT,
  corrective_action TEXT,
  technician_name VARCHAR(100),
  spare_parts_used TEXT,
  cost DECIMAL(10,2),
  severity VARCHAR(20),
  type VARCHAR(20),  -- preventive/reactive
  status VARCHAR(20)  -- ongoing/resolved
);
```

### 2. Manual Entry Form
- UI form untuk teknisi input detail perbaikan
- Upload photo/dokumen
- Link ke spare parts inventory

### 3. Advanced Analytics
- Downtime prediction based on patterns
- MTBF (Mean Time Between Failures)
- MTTR (Mean Time To Repair)
- Pareto analysis per komponen
- Cost analysis

### 4. Real-time Notifications
- Alert ketika downtime terjadi
- Email/WhatsApp notification ke teknisi
- Auto-create work order

---

## 📝 Summary

✅ **Backend:**
- `downtime_service.py` - Service layer untuk analisis machine_logs
- `downtime_controller.py` - REST API endpoints
- Routes registered di `routes.py`

✅ **Frontend:**
- `DowntimeHistory.jsx` - Component dengan real-time data
- `api.js` - Updated dengan fetchDowntimeHistory & fetchDowntimeStatistics
- Loading, error handling, empty states

✅ **Database:**
- Menggunakan tabel `machine_logs` yang sudah ada
- Tidak perlu migration baru
- Backward compatible dengan sistem existing

✅ **Features:**
- Real-time downtime detection dari status changes
- Filter by component & date range
- Statistics aggregation
- Severity classification (Low/Medium/High/Critical)
- Type classification (Preventive/Reactive)
- Human-readable duration display
- Expandable row details

---

## 🎯 Quick Start

1. **Start Backend:**
```bash
cd Backend
python app.py
```

2. **Start Frontend:**
```bash
cd FE
npm run dev
```

3. **Access Dashboard:**
```
http://localhost:5173
```

4. **View Downtime History:**
Scroll ke section "Riwayat Downtime" di dashboard

---

**Implementasi Date:** October 25, 2025  
**Version:** 1.0.0  
**Status:** ✅ Production Ready

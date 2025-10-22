# 🚀 Quick Start Guide - FlexoTwin Dashboard

## 📋 Prerequisites

- Python 3.12+
- Node.js 20.15+
- PostgreSQL (Supabase)
- MQTT Broker (optional)

---

## 🔥 **Running the Application**

### **Step 1: Start Backend (Flask)**

Open terminal/PowerShell dan jalankan:

```powershell
# Terminal 1 - Backend
cd "c:\Users\HP\Documents\Belajar python\Digital Twin\Sistem2\Backend"
python app.py
```

**Expected Output:**

```
======================================================================
🚀 STARTING FLEXOTWIN BACKEND SERVER
======================================================================
Server running at: http://0.0.0.0:5000
API Documentation: http://0.0.0.0:5000/api/docs
Health Check: http://0.0.0.0:5000/health
Press CTRL+C to stop the server
```

✅ Backend akan running di: **http://localhost:5000**

---

### **Step 2: Start Frontend (React + Vite)**

Open terminal/PowerShell baru dan jalankan:

```powershell
# Terminal 2 - Frontend
cd "c:\Users\HP\Documents\Belajar python\Digital Twin\Sistem2\Frontend"
npm run dev
```

**Expected Output:**

```
  VITE v7.1.11  ready in 1843 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

✅ Frontend akan running di: **http://localhost:5173**

---

### **Step 3: Start MQTT Simulator (Optional)**

Untuk simulasi data sensor real-time:

```powershell
# Terminal 3 - Sensor Simulator
cd "c:\Users\HP\Documents\Belajar python\Digital Twin\Sistem2\Sensor"
python sensor_simulator.py
```

---

## ✅ **Verification Checklist**

### 1. **Check Backend Health**

```powershell
curl http://localhost:5000/health
```

**Expected Response:**

```json
{
  "status": "healthy",
  "service": "FlexoTwin Backend API",
  "version": "1.0.0",
  "mqtt_connected": true
}
```

### 2. **Check Component Health API**

```powershell
curl http://localhost:5000/api/health/Pre-Feeder
```

**Expected Response:**

```json
{
  "component": "Pre-Feeder",
  "health_index": 85.5,
  "status": "Sehat",
  "color": "#10B981",
  "oee": 90.2,
  "availability_rate": 92.0,
  "performance_rate": 95.0,
  "quality_rate": 98.5
}
```

### 3. **Check Frontend Connection**

Open browser: **http://localhost:5173**

**Expected:**

- ✅ Dashboard loads successfully
- ✅ Component cards show health data
- ✅ OEE charts display data
- ✅ Trend chart shows lines
- ✅ No connection errors

---

## 🐛 **Troubleshooting**

### Problem 1: Dashboard shows "0.00%" everywhere

**Cause:** Backend tidak running atau tidak terkoneksi

**Solution:**

```powershell
# Check backend status
curl http://localhost:5000/health

# Jika error, start backend:
cd Backend
python app.py
```

### Problem 2: "Failed to connect to backend" error

**Cause:** CORS atau backend tidak accessible

**Solution:**

1. Pastikan backend running di port 5000
2. Check CORS sudah enable di `Backend/app.py`
3. Check firewall tidak block port 5000

### Problem 3: MQTT data tidak muncul

**Cause:** MQTT service belum running atau database kosong

**Solution:**

```powershell
# Start sensor simulator untuk generate data
cd Sensor
python sensor_simulator.py
```

### Problem 4: Frontend tidak load

**Cause:** Dependencies belum terinstall atau port conflict

**Solution:**

```powershell
# Install dependencies
cd Frontend
npm install

# Run on different port if 5173 is busy
npm run dev -- --port 3000
```

---

## 📊 **Expected Dashboard Sections**

Setelah backend dan frontend running, dashboard harus menampilkan:

### ✅ **Section 1: Overall Statistics** (Top)

- Total Components: 5
- Healthy Components: 3-5 (based on data)
- Need Attention: 0-2 (based on data)
- Overall Health: 70-95% (average)

### ✅ **Section 2: Component Health Cards**

5 cards dengan data:

- Pre-Feeder: Health Index + OEE metrics
- Feeder: Health Index + OEE metrics
- Printing: Health Index + OEE metrics
- Slotter: Health Index + OEE metrics
- Stacker: Health Index + OEE metrics

### ✅ **Section 3: OEE Analysis**

- 4 metric cards (OEE, Availability, Performance, Quality)
- Bar chart showing OEE components
- Line chart showing OEE trend
- Analysis & recommendations

### ✅ **Section 4: Health Trend Chart**

- Multi-line chart with 5 colored lines
- Shows last 50 data points
- Statistics per component

### ✅ **Section 5: Prediction Panel** (Sidebar)

- Input form for prediction
- Submit button
- Results display

### ✅ **Section 6: FMEA Analysis**

- Component dropdown selector
- FMEA table with expandable rows
- RPN scores and recommendations

---

## 🔄 **Data Flow**

```
MQTT Broker (Sensor Data)
    ↓
Backend Flask (app.py)
    ├→ Store in PostgreSQL
    ├→ Calculate Health Index
    ├→ Calculate OEE
    └→ Expose via REST API
         ↓
Frontend React (localhost:5173)
    ├→ Fetch every 5 seconds
    ├→ Update state
    ├→ Render components
    └→ Display charts
```

---

## 📝 **API Endpoints Used by Frontend**

| Endpoint                   | Method | Purpose                   |
| -------------------------- | ------ | ------------------------- |
| `/api/health/<component>`  | GET    | Get component health data |
| `/api/predict/maintenance` | POST   | Run ML prediction         |

---

## 🎯 **Testing Checklist**

- [ ] Backend starts without errors
- [ ] Backend health endpoint returns 200
- [ ] Frontend loads at localhost:5173
- [ ] No CORS errors in browser console
- [ ] Component cards show real data (not 0.00%)
- [ ] OEE charts display bars and lines
- [ ] Trend chart shows multiple lines
- [ ] Prediction panel accepts input
- [ ] FMEA table loads with data
- [ ] Auto-refresh works (data updates every 5s)

---

## 🚀 **Quick Commands**

```powershell
# Terminal 1 - Backend
cd Backend && python app.py

# Terminal 2 - Frontend
cd Frontend && npm run dev

# Terminal 3 - Sensor Simulator (Optional)
cd Sensor && python sensor_simulator.py

# Check Backend
curl http://localhost:5000/health

# Check API
curl http://localhost:5000/api/health/Pre-Feeder
```

---

## 📞 **Ports Summary**

| Service        | Port | URL                   |
| -------------- | ---- | --------------------- |
| Backend Flask  | 5000 | http://localhost:5000 |
| Frontend React | 5173 | http://localhost:5173 |
| PostgreSQL     | 5432 | (Supabase Cloud)      |
| MQTT Broker    | 1883 | broker.hivemq.com     |

---

## ✨ **Expected Result**

Setelah kedua server running, dashboard akan:

- ✅ Menampilkan health index untuk 5 komponen
- ✅ Menampilkan OEE breakdown dengan charts
- ✅ Menampilkan trend lines untuk historical data
- ✅ Auto-refresh setiap 5 detik
- ✅ Prediksi maintenance berfungsi
- ✅ FMEA analysis interaktif

**Dashboard seharusnya tidak menampilkan 0.00% lagi!** 🎉

---

**Last Updated:** October 22, 2025  
**Version:** 1.0.0  
**Support:** Check logs di terminal untuk debugging

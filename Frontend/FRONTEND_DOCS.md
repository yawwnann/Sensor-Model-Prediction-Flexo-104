# 🚀 FlexoTwin Frontend - Quick Start Guide

## 📋 Overview

Frontend **FlexoTwin Smart Maintenance 4.0** - Real-time machine health monitoring dashboard.

**Tech Stack:**

- ⚛️ React 18 + Vite
- 🎨 Tailwind CSS
- 📊 Lucide Icons
- 🔌 Axios

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
npm install
```

### 2. Start Development Server

```bash
npm run dev
```

Dashboard: **http://localhost:5173**

### 3. Ensure Backend is Running

```bash
cd ../Backend
python app.py
```

Backend API: **http://localhost:5000**

---

## 📁 Project Structure

```
src/
├── components/
│   ├── ComponentCard.jsx       # Health status card
│   └── PredictionPanel.jsx     # ML prediction panel
├── services/
│   └── api.js                  # API service layer
├── App.jsx                     # Main app
├── App.css                     # Styles
└── main.jsx                    # Entry point
```

---

## 🎯 Features

### ✅ Real-time Monitoring

- Auto-refresh every 5 seconds
- 5 machine components: Pre-Feeder, Feeder, Printing, Slotter, Stacker
- Health Index with OEE metrics

### ✅ ML Prediction

- Maintenance duration prediction
- Input: Total produksi & produk cacat
- Output: Prediksi durasi (menit)

### ✅ Visual Indicators

- 🟢 Health >= 80%: Healthy
- 🟡 Health 60-79%: Warning
- 🔴 Health < 60%: Critical

---

## 🔌 API Endpoints

### Get Component Health

```
GET /api/health/{component_name}
```

### Run Prediction

```
POST /api/predict/maintenance
Body: {
  "total_produksi": 10000,
  "produk_cacat": 500
}
```

---

## 🐛 Troubleshooting

### Backend Connection Error

```bash
# Check backend is running
curl http://localhost:5000/health
```

### CORS Error

```bash
# Install flask-cors in backend
cd Backend
pip install flask-cors
```

### Port Conflict

```bash
# Run on different port
npm run dev -- --port 3000
```

---

## 📦 Scripts

```bash
npm run dev      # Start dev server
npm run build    # Build for production
npm run preview  # Preview production build
npm run lint     # Run ESLint
```

---

## 📚 Documentation

Full documentation: [Frontend/FRONTEND_DOCS.md](./FRONTEND_DOCS.md)

---

**FlexoTwin Smart Maintenance 4.0** | React + Vite Template

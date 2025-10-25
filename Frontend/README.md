# Digital Twin Flexo Machine C_FL104 - Frontend

> **Real-time Monitoring & Predictive Maintenance System**  
> Versi: 2.0 | Tanggal: Oktober 2025

## 📋 Overview

Frontend aplikasi untuk monitoring dan prediksi maintenance mesin Flexo C_FL104. Aplikasi ini terintegrasi dengan backend Flask dan ML model untuk memberikan insights real-time tentang kondisi mesin.

## ✨ Features

### 🎯 Real-time Machine Monitoring
- **Component Health Status**: Monitoring 5 komponen utama (Pre-Feeder, Feeder, Printing, Slotter, Stacker)
- **Interactive Machine Diagram**: Hotspots interaktif pada diagram mesin
- **Overall Machine Health**: Indikator kesehatan keseluruhan mesin C_FL104
- **Status Indicators**: Color-coded status (Good, Warning, Critical)

### 🤖 Predictive Maintenance (ML-Based)
- **Auto-Prediction Trigger**: Otomatis trigger saat overall health < 40%
- **Maintenance Duration Prediction**: Estimasi durasi maintenance untuk KESELURUHAN MESIN
- **Confidence Score**: Tingkat kepercayaan prediksi (85-95%)
- **Risk Assessment**: Level risiko berdasarkan kondisi mesin

### 📊 Data Visualization
- **Health Trends Chart**: Tren kesehatan komponen over time
- **OEE Chart**: Overall Equipment Effectiveness visualization
- **Real-time Updates**: Auto-refresh setiap 5 detik
- **Historical Data**: Tracking performa hingga 50 data points

### 🔍 FMEA Analysis
- **Failure Mode Analysis**: Analisis mode kegagalan per komponen
- **RPN Calculation**: Risk Priority Number (Severity × Occurrence × Detection)
- **Recommended Actions**: Rekomendasi tindakan berdasarkan RPN

### � Downtime History
- **Historical Records**: Riwayat downtime mesin dengan detail lengkap
- **Duration Tracking**: Total dan rata-rata durasi downtime
- **Component Breakdown**: Filter downtime per komponen
- **Statistics Summary**: Preventive vs Reactive maintenance count
- **Root Cause Analysis**: Alasan dan tindakan yang diambil

### �🔔 Alert System
- **Auto-Prediction Alert**: Banner alert untuk maintenance prediction
- **Critical Component Alerts**: Notifikasi komponen critical
- **Connection Status**: Monitor koneksi ke backend

## 🛠 Technology Stack

| Teknologi        | Versi   | Purpose                      |
| ---------------- | ------- | ---------------------------- |
| **React**        | 19.1.1  | Frontend framework           |
| **Vite**         | 7.1.7   | Build tool & dev server      |
| **TailwindCSS**  | 4.1.15  | Styling framework            |
| **Recharts**     | 3.3.0   | Charts & visualization       |
| **Axios**        | 1.12.2  | HTTP client                  |
| **Lucide React** | 0.546.0 | Icon library                 |
| **React Router** | 7.1.1   | Routing                      |

## 📦 Installation

### Prerequisites
- Node.js 18+ and npm
- Backend Flask server running (port 5000)
- PostgreSQL database configured

### Steps

1. **Clone the repository**
```bash
git clone [repository-url]
cd Sensor-Model-Prediction-Flexo-104-main/FE
```

2. **Install dependencies**
```bash
npm install
```

3. **Configure environment**
```bash
# Create .env file
echo "VITE_API_BASE_URL=http://localhost:5000/api" > .env
```

4. **Start development server**
```bash
npm run dev
```

Application will be available at `http://localhost:5173`

## 🚀 Usage

### Development Mode
```bash
npm run dev
```

### Build for Production
```bash
npm run build
```

### Preview Production Build
```bash
npm run preview
```

## 🏗 Project Structure

```
FE/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── AutoPredictionAlert.jsx
│   │   ├── ComponentCard.jsx
│   │   ├── DowntimeHistory.jsx
│   │   ├── FMEATable.jsx
│   │   ├── Hotspot.jsx
│   │   ├── HotspotPopover.jsx
│   │   ├── Navbar.jsx
│   │   ├── OEEChart.jsx
│   │   └── TrendChart.jsx
│   ├── pages/               # Page components
│   │   └── DashboardPage.jsx
│   ├── services/            # API services
│   │   └── api.js
│   ├── utils/               # Utility functions
│   │   └── helpers.js
│   ├── App.jsx              # Main app component
│   └── main.jsx             # Entry point
├── public/                  # Static assets
│   └── tcy_flexo_machine_2.png
├── .env                     # Environment variables
├── vite.config.js          # Vite configuration
├── tailwind.config.js      # Tailwind configuration
├── package.json            # Dependencies
├── README.md               # This file
├── FRONTEND_IMPLEMENTATION.md   # Implementation details
└── KONSEP_PREDIKSI_MESIN.md    # ML prediction concepts
```

## 🔧 Configuration

### Environment Variables

Create `.env` file in root directory:

```env
# Backend API URL
VITE_API_BASE_URL=http://localhost:5000/api

# Optional: Custom port for dev server
# VITE_PORT=5173
```

### API Endpoints

Frontend menggunakan endpoints berikut (defined in `api.js`):

| Endpoint                    | Method | Purpose                             |
| --------------------------- | ------ | ----------------------------------- |
| `/health/machine`           | GET    | Overall machine health + prediction |
| `/health/components`        | GET    | All components health breakdown     |
| `/health/:componentName`    | GET    | Specific component health           |
| `/sensor/latest`            | GET    | Latest sensor readings              |
| `/sensor/history?limit=50`  | GET    | Historical sensor data              |
| `/predict/maintenance`      | POST   | Manual maintenance prediction       |
| `/predict/history`          | GET    | Prediction history                  |
| `/downtime/history`         | GET    | Downtime history records            |
| `/downtime/statistics`      | GET    | Downtime statistics summary         |
| `/info`                     | GET    | System information                  |

## 🎯 Key Concepts

### Machine-Level Prediction

**IMPORTANT**: Model ML memprediksi maintenance untuk **KESELURUHAN MESIN C_FL104**, bukan per komponen.

```javascript
// ✅ CORRECT: Prediction untuk seluruh mesin
const prediction = await predictMaintenance({
  machine_id: "C_FL104",
  input_data: {
    total_production: 15234,    // Total dari seluruh mesin
    defect_count: 234,          // Total dari seluruh mesin
    performance_rate: 87.5,     // Performance seluruh mesin
    // ...
  }
});

// Output: "12 jam 1 menit" untuk maintenance SELURUH mesin
```

**Alasan:**
1. Interdependensi komponen
2. Efisiensi operasional
3. Data training model untuk keseluruhan mesin
4. Industry best practice (comprehensive maintenance)
5. Cost effectiveness

Baca detail lengkap di: [`KONSEP_PREDIKSI_MESIN.md`](./KONSEP_PREDIKSI_MESIN.md)

### Auto-Prediction Trigger

```javascript
// Trigger otomatis ketika overall machine health < 40%
if (overallMachineHealth < 40) {
  // Backend auto-trigger prediction
  // Frontend menampilkan alert
}
```

### Component Monitoring

Component cards menampilkan health per komponen untuk:
- Monitoring detail
- Identifikasi prioritas
- Breakdown analisis

**Note**: Ini untuk monitoring saja, bukan prediction per komponen.

## 📱 UI Components

### DashboardPage
Main dashboard dengan:
- Navbar dengan machine ID & overall health
- Auto-prediction alert banner
- Machine diagram carousel (6 views)
- Component health cards grid
- Health trends chart
- OEE chart
- FMEA analysis table

### AutoPredictionAlert
Global alert untuk maintenance prediction:
- Displays ketika overall health < 40%
- Shows maintenance duration estimate
- Lists critical components
- Confidence score indicator
- Dismissable

### ComponentCard
Individual component status card:
- Health index (0-100)
- Status badge (Good/Warning/Critical)
- OEE metrics
- Recommendations (collapsible)

### Charts
- **TrendChart**: Line chart untuk health trends
- **OEEChart**: Bar chart untuk OEE metrics

### FMEATable
FMEA analysis dengan:
- Component selector
- RPN calculation & color coding
- Expandable rows untuk recommendations
- Static FMEA data

## 🔄 Data Flow

```
Backend (Flask) ← MQTT ← Sensor Simulator
     ↓
  REST API
     ↓
Frontend (React)
     ↓
   User Display
```

### Real-time Updates

```javascript
// Auto-refresh every 5 seconds
const REFRESH_INTERVAL = 5000;

useEffect(() => {
  fetchData();
  const interval = setInterval(fetchData, REFRESH_INTERVAL);
  return () => clearInterval(interval);
}, []);
```

## 🐛 Troubleshooting

### Backend Connection Error

**Problem**: "Cannot connect to backend"

**Solutions**:
1. Ensure Flask server is running: `python app.py`
2. Check backend is on `http://localhost:5000`
3. Verify `.env` file has correct `VITE_API_BASE_URL`
4. Check CORS settings in backend

### Data Not Updating

**Problem**: Dashboard shows stale data

**Solutions**:
1. Check MQTT broker connection
2. Verify sensor simulator is running
3. Check browser console for errors
4. Manual refresh using refresh button

### Chart Not Displaying

**Problem**: Charts are empty

**Solutions**:
1. Wait for data to accumulate (need at least 2 data points)
2. Check API responses in Network tab
3. Verify data format from backend

## 📚 Documentation

- **Main Documentation**: [`../DOKUMENTASI.md`](../DOKUMENTASI.md)
- **Implementation Guide**: [`FRONTEND_IMPLEMENTATION.md`](./FRONTEND_IMPLEMENTATION.md)
- **Prediction Concepts**: [`KONSEP_PREDIKSI_MESIN.md`](./KONSEP_PREDIKSI_MESIN.md)
- **Backend Docs**: [`../Backend/Documentation/README.md`](../Backend/Documentation/README.md)

## 🤝 Contributing

1. Fork the repository
2. Create feature branch: `git checkout -b feature/AmazingFeature`
3. Commit changes: `git commit -m 'Add AmazingFeature'`
4. Push to branch: `git push origin feature/AmazingFeature`
5. Open Pull Request

## 📄 License

This project is part of academic research for predictive maintenance system.

## 👥 Authors

- Frontend Development Team
- Machine Learning Team
- Backend Development Team

## 🙏 Acknowledgments

- Based on real Flexo machine data (12 months historical)
- Integrated with Random Forest ML model
- Real-time MQTT data streaming

---

**Machine ID**: C_FL104  
**System Version**: 2.0  
**Last Updated**: October 24, 2025

For questions or support, please refer to the main documentation or contact the development team.

## Project Structure

```
src/
├── api/
│   └── authService.js      # Authentication service
├── assets/
│   └── react.svg          # Static assets
├── components/
│   ├── AIProcessorCard.jsx    # ML prediction component
│   ├── ComponentCard.jsx      # Machine component display
│   ├── Header.jsx            # Application header
│   ├── HistoryModal.jsx      # Historical data viewer
│   ├── Hotspot.jsx          # Interactive machine points
│   ├── HotspotPopover.jsx   # Hotspot information display
│   ├── Icons.jsx            # SVG icons
│   ├── SummaryPanel.jsx     # Status summary
│   └── YearlyHealthChart.jsx # Annual health trends
├── data/
│   └── mockData.js         # Demo data
├── pages/
│   ├── DashboardPage.jsx    # Main dashboard
│   ├── LoginPage.jsx        # User login
│   └── RegisterPage.jsx     # User registration
└── utils/
    └── helpers.js          # Utility functions
```

## Usage

1. **Login/Register**
   - Use credentials to access the system
   - New users can register for access

2. **Dashboard Navigation**
   - View machine components status
   - Interact with hotspots for detailed info
   - Monitor real-time health scores

3. **Predictive Analysis**
   - Upload CSV files for analysis
   - View prediction results
   - Generate prediction reports

4. **Historical Data**
   - Access past performance data
   - View yearly trends
   - Generate annual reports

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
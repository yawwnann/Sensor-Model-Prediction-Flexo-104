# 📊 FlexoTwin Dashboard Guide

## Overview

FlexoTwin menyediakan **2 jenis dashboard** untuk monitoring real-time:

1. **Streamlit Dashboard** (`dashboard.py`) - Original dashboard
2. **Dash Dashboard** (`dashboard_dash.py`) - New enterprise-grade dashboard

---

## 🎯 Streamlit Dashboard

### Fitur Utama

- ✅ Auto-refresh setiap 5 detik dengan cache optimization
- 📊 5 Section monitoring lengkap
- 🔧 Modul prediksi maintenance terintegrasi
- 📈 OEE breakdown (Availability, Performance, Quality)
- 📉 Grafik trend real-time
- 🔍 Analisis FMEA per komponen

### Cara Menjalankan

```powershell
# Pastikan backend Flask sudah running di port 5000
cd "c:\Users\HP\Documents\Belajar python\Digital Twin\Sistem2"
streamlit run dashboard.py
```

### Port

- Dashboard: http://localhost:8501
- Backend API: http://localhost:5000

### Kelebihan

- UI/UX friendly dan interaktif
- Setup cepat dan mudah
- Best untuk development dan testing
- Built-in caching mechanism

---

## 🚀 Dash Dashboard (NEW)

### Fitur Utama

- ✅ Semua fitur Streamlit + lebih enterprise-grade
- 🎨 Bootstrap 5 styling dengan responsif design
- 📱 Mobile-friendly layout
- ⚡ Better performance untuk production
- 🔄 Interval-based callbacks (no continuous polling)
- 🎯 Modular component architecture

### Cara Menjalankan

```powershell
# Pastikan backend Flask sudah running di port 5000
cd "c:\Users\HP\Documents\Belajar python\Digital Twin\Sistem2"
python dashboard_dash.py
```

### Port

- Dashboard: http://localhost:8050
- Backend API: http://localhost:5000

### Kelebihan

- Production-ready
- Better scalability
- Custom CSS support
- Deploy-friendly (support WSGI servers)
- Callback-based updates (more efficient)

---

## 🔧 Dependencies

### Streamlit Dashboard

```txt
streamlit==1.31.0
requests==2.31.0
plotly==5.18.0
pandas==2.2.0
```

### Dash Dashboard

```txt
dash==2.14.2
dash-bootstrap-components==1.5.0
plotly==5.18.0
requests==2.31.0
```

### Install Dash Dependencies

```powershell
pip install dash dash-bootstrap-components
```

---

## 📊 Section Dashboard

Kedua dashboard memiliki section yang sama:

### 1. Ringkasan Kondisi Mesin

- Overall Health Index
- Overall OEE
- Availability, Performance, Quality metrics
- Status indicator (Optimal/Warning/Danger)

### 2. Komponen OEE Detail

- Breakdown Availability, Performance, Quality
- Bar chart comparison per komponen
- Trend OEE historis
- Analisis dan rekomendasi

### 3. Status Kesehatan per Komponen

- Health index untuk 5 komponen:
  - Pre-Feeder
  - Feeder
  - Printing
  - Slotter
  - Stacker
- Color-coded status (hijau/kuning/merah)

### 4. Grafik Tren dan Log Historis

- Line chart untuk semua komponen (50 data points)
- Tabel log status terakhir
- Hover info untuk detail

### 5. Analisis Akar Masalah (FMEA)

- Tabel FMEA per komponen
- Failure Mode, Root Cause, Effect
- RPN calculation (Severity × Occurrence × Detection)
- Komponen selection dropdown

---

## 🔮 Modul Prediksi Maintenance

### Input

- Total Produksi (Pcs)
- Produk Cacat (Pcs)

### Output

- Prediksi durasi maintenance dalam menit
- Color-coded alert:
  - 🟢 < 30 menit: Normal
  - 🟡 30-60 menit: Warning
  - 🔴 > 60 menit: Danger

### API Endpoint

```
POST http://localhost:5000/api/predict/maintenance
Body: {
  "total_produksi": 10000,
  "produk_cacat": 500
}
```

---

## ⚙️ Configuration

### Environment Variables

```bash
# API Configuration
API_BASE_URL=http://localhost:5000/api/health
PREDICT_API_URL=http://localhost:5000/api/predict/maintenance

# Refresh Configuration
REFRESH_SECONDS=5
REQUEST_TIMEOUT=12
MAX_RETRIES=2
```

### Ubah Refresh Interval

**Streamlit:**

```python
# dashboard.py line ~25
REFRESH_SECONDS = 5  # ubah sesuai kebutuhan
```

**Dash:**

```python
# dashboard_dash.py line ~58
REFRESH_SECONDS = 5  # ubah sesuai kebutuhan
```

---

## 🚦 Running Both Dashboards

Anda bisa menjalankan kedua dashboard secara bersamaan:

```powershell
# Terminal 1: Backend Flask
cd Backend
python app.py

# Terminal 2: Streamlit Dashboard
cd ..
streamlit run dashboard.py

# Terminal 3: Dash Dashboard
python dashboard_dash.py
```

Akses:

- Backend API: http://localhost:5000
- Streamlit: http://localhost:8501
- Dash: http://localhost:8050

---

## 📈 Performance Comparison

| Feature           | Streamlit  | Dash       |
| ----------------- | ---------- | ---------- |
| Development Speed | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐   |
| Production Ready  | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ |
| Customization     | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ |
| Performance       | ⭐⭐⭐⭐   | ⭐⭐⭐⭐⭐ |
| Mobile Support    | ⭐⭐⭐     | ⭐⭐⭐⭐⭐ |
| Learning Curve    | Easy       | Medium     |

---

## 🐛 Troubleshooting

### Dashboard tidak muncul data

1. Pastikan backend Flask running
2. Check API endpoint: http://localhost:5000/api/health/Pre-Feeder
3. Check console untuk error messages

### Error "Connection refused"

```bash
# Restart backend
cd Backend
python app.py
```

### Dashboard freeze

- Streamlit: Tekan 'R' untuk reload
- Dash: Refresh browser (Ctrl+F5)

### Port already in use

```powershell
# Streamlit
streamlit run dashboard.py --server.port 8502

# Dash
# Edit dashboard_dash.py line terakhir:
app.run_server(debug=True, port=8051)
```

---

## 🎯 Best Practices

### Development

- Gunakan **Streamlit** untuk rapid prototyping
- Testing lebih cepat dengan auto-reload
- Interactive debugging di browser

### Production

- Gunakan **Dash** untuk deployment
- Deploy dengan Gunicorn + Nginx
- Better resource management
- Scalable architecture

### Monitoring

- Set refresh interval sesuai beban server
- Monitor backend logs untuk error tracking
- Use caching untuk optimize performance

---

## 📚 Additional Resources

### Documentation

- Streamlit: https://docs.streamlit.io/
- Dash: https://dash.plotly.com/
- Flask: https://flask.palletsprojects.com/

### Related Files

- `Backend/src/controllers/prediction_controller.py` - ML prediction endpoint
- `Backend/src/services/prediction_service.py` - Prediction service
- `Model/predict.py` - Standalone prediction script
- `Backend/Documentation/ML_INTEGRATION.md` - ML integration guide

---

## 🎉 Conclusion

**Pilih dashboard sesuai kebutuhan:**

- 🧪 **Development/Testing** → Streamlit (`dashboard.py`)
- 🚀 **Production/Enterprise** → Dash (`dashboard_dash.py`)

Kedua dashboard memiliki fitur lengkap dan sudah production-ready!

---

**Last Updated:** 2025-01-XX  
**Version:** 2.0  
**Author:** FlexoTwin Development Team

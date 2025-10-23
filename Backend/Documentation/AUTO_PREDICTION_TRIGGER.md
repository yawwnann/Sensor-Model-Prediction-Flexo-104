# Auto-Prediction Trigger Feature

## 📋 Deskripsi

Fitur **Auto-Prediction Trigger** adalah sistem pemicu otomatis untuk prediksi maintenance berdasarkan kondisi kesehatan mesin. Sistem ini secara otomatis menjalankan prediksi ML ketika **Health Index** mesin turun di bawah ambang batas kritis.

## 🎯 Tujuan

- **Proaktif**: Mendeteksi kondisi kritis secara otomatis tanpa intervensi manual
- **Preventif**: Memberikan prediksi maintenance sebelum terjadi breakdown
- **Efisien**: Mengurangi ketergantungan pada tombol manual di dashboard

## ⚙️ Cara Kerja

### 1. Monitoring Kesehatan

Setiap kali endpoint `/api/health/<component>` dipanggil, sistem akan:

- Menghitung **Final Health Index** berdasarkan RPN dan OEE
- Membandingkan nilai dengan **Critical Threshold**

### 2. Pemicu Otomatis

Jika `final_health_index < CRITICAL_THRESHOLD` (40.0):

- Sistem secara otomatis memanggil **PredictionService**
- Menggunakan data sensor terbaru dari database
- Jika tidak ada data, menggunakan nilai default tipikal

### 3. Input Default

Sistem mengambil input dari:

```python
# Prioritas 1: Data sensor terbaru dari database
recent_logs = db_service.get_recent_machine_logs(limit=1)
total_produksi = latest_log.get("total_production", 5000)
produk_cacat = latest_log.get("defect_count", 100)

# Prioritas 2: Nilai default fallback
default_input = {
    "total_produksi": 5000,
    "produk_cacat": 150
}
```

## 📊 Konfigurasi

### Critical Threshold

Didefinisikan di `health_service.py`:

```python
CRITICAL_THRESHOLD = 40.0  # Health Index threshold
```

**Interpretasi:**

- `>= 90`: Excellent (Hijau Tua)
- `>= 80`: Good (Hijau)
- `>= 70`: Fair (Hijau Muda)
- `>= 50`: Poor (Orange)
- `< 50`: Critical (Merah)
- `< 40`: **AUTO-TRIGGER ACTIVATED** 🚨

### Mengubah Threshold

Untuk mengubah ambang batas pemicu:

1. Edit file `Backend/src/services/health_service.py`
2. Ubah nilai `CRITICAL_THRESHOLD` sesuai kebutuhan
3. Restart server

```python
# Contoh: Pemicu lebih sensitif
CRITICAL_THRESHOLD = 50.0  # Trigger saat Poor

# Contoh: Pemicu hanya untuk kondisi sangat kritis
CRITICAL_THRESHOLD = 30.0  # Trigger saat extremely critical
```

## 🔍 Response Format

### Normal Response (Health Index >= 40)

```json
{
  "component_name": "Printing Unit",
  "health_index": 65.5,
  "status": "Fair",
  "metrics": { ... }
}
```

### Auto-Triggered Response (Health Index < 40)

```json
{
  "component_name": "Printing Unit",
  "health_index": 35.2,
  "status": "Critical",
  "metrics": { ... },
  "auto_prediction": {
    "triggered": true,
    "trigger_threshold": 40.0,
    "prediction_result": {
      "success": true,
      "prediction": 127.5,
      "prediction_formatted": "2 jam 7 menit",
      "input": {
        "total_produksi": 5000,
        "produk_cacat": 150
      },
      "message": "Prediksi berhasil",
      "metadata": { ... }
    }
  }
}
```

## 📝 Logging

### Log Level: WARNING

Semua pemicu otomatis dicatat dengan level `WARNING` untuk visibilitas tinggi:

#### 1. Deteksi Critical Health

```
⚠️ CRITICAL HEALTH DETECTED! Health Index: 35.2 < 40.0
```

#### 2. Pemicu Prediksi

```
🤖 Auto-triggering maintenance prediction with input: {'total_produksi': 5000, 'produk_cacat': 150}
```

#### 3. Hasil Sukses

```
✅ AUTO-PREDICTION COMPLETED |
   Health Index: 35.2 |
   Predicted Maintenance Duration: 2 jam 7 menit |
   Input: Total Produksi=5000, Produk Cacat=150 |
   RECOMMENDATION: Schedule immediate maintenance!
```

#### 4. Hasil Gagal

```
❌ AUTO-PREDICTION FAILED |
   Health Index: 35.2 |
   Error: Model tidak tersedia
```

### Melihat Log

```bash
# Di terminal
tail -f Backend/logs/app.log | grep "AUTO"

# Atau filter untuk WARNING level
tail -f Backend/logs/app.log | grep "WARNING"
```

## 🔧 Implementasi Detail

### Lokasi Kode

- **Service Layer**: `Backend/src/services/health_service.py`

  - Fungsi: `calculate_component_health()`
  - Logika pemicu ada di dalam fungsi ini

- **Controller Layer**: `Backend/src/controllers/health_controller.py`
  - Endpoint: `GET /api/health/<component_name>`
  - Menambahkan `auto_prediction` ke response

### Lazy Loading

PredictionService di-load secara lazy untuk menghindari circular import:

```python
def _get_prediction_service(self):
    if self._prediction_service is None:
        from src.services.prediction_service import PredictionService
        self._prediction_service = PredictionService()
    return self._prediction_service
```

## 🧪 Testing

### 1. Test Manual dengan Critical Health

Untuk mensimulasikan kondisi kritis:

```bash
# Jalankan sensor simulator dengan nilai yang menghasilkan health index rendah
python Sensor/sensor_simulator.py
```

### 2. Test dengan Modifikasi Threshold

Ubah `CRITICAL_THRESHOLD` ke nilai lebih tinggi untuk testing:

```python
CRITICAL_THRESHOLD = 80.0  # Test mode - trigger lebih mudah
```

### 3. Monitor Log Real-time

```bash
# Terminal 1: Jalankan server
cd Backend
python app.py

# Terminal 2: Monitor log
tail -f Backend/logs/app.log
```

### 4. Test API Call

```bash
# Panggil health endpoint
curl http://localhost:5000/api/health/Printing%20Unit

# Periksa apakah response mengandung "auto_prediction"
```

## 📈 Flow Diagram

```
┌─────────────────────────┐
│  Dashboard/Frontend     │
│  Calls Health Endpoint  │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Health Controller      │
│  GET /api/health/<comp> │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Health Service         │
│  calculate_health()     │
└───────────┬─────────────┘
            │
            ▼
┌─────────────────────────┐
│  Check: Health < 40?    │
└───────┬─────────┬───────┘
        │         │
    NO  │         │ YES
        │         │
        ▼         ▼
    ┌───────┐  ┌──────────────────────┐
    │Return │  │ AUTO-TRIGGER:        │
    │Normal │  │ 1. Get latest data   │
    │Result │  │ 2. Call Prediction   │
    └───────┘  │ 3. Log result        │
               │ 4. Add to response   │
               └──────────────────────┘
```

## 🚨 Troubleshooting

### Issue: Prediksi tidak terpicu meskipun health < 40

**Kemungkinan Penyebab:**

1. Model tidak ter-load dengan benar
2. Database tidak memiliki data sensor

**Solusi:**

```bash
# 1. Periksa log untuk error
tail -f Backend/logs/app.log | grep -i error

# 2. Periksa model
curl http://localhost:5000/api/model/info

# 3. Periksa database connection
curl http://localhost:5000/api/health
```

### Issue: Log tidak muncul

**Solusi:**

```python
# Periksa logger configuration di utils/logger.py
# Pastikan level minimal adalah WARNING
```

## 💡 Best Practices

### 1. Monitoring

- Setup monitoring untuk log dengan keyword "AUTO-TRIGGER"
- Alert tim maintenance saat pemicu otomatis terjadi

### 2. Threshold Tuning

- Monitor false positives/negatives
- Adjust `CRITICAL_THRESHOLD` berdasarkan histori
- Dokumentasikan perubahan threshold

### 3. Data Quality

- Pastikan sensor data selalu up-to-date
- Validasi data sensor sebelum digunakan untuk prediksi

### 4. Feedback Loop

- Catat waktu pemicu vs actual maintenance
- Gunakan untuk meningkatkan akurasi model

## 🔄 Integration dengan Dashboard

### Frontend dapat:

1. **Menampilkan badge "Auto-Predicted"** jika `auto_prediction.triggered === true`
2. **Highlight maintenance prediction** yang dipicu otomatis
3. **Menampilkan timestamp pemicu** untuk audit trail
4. **Alert operator** dengan notifikasi khusus

### Contoh UI Integration (React):

```jsx
{
  healthData.auto_prediction?.triggered && (
    <Alert severity="warning">
      <AlertTitle>⚠️ Automatic Prediction Triggered</AlertTitle>
      Health Index dropped below {healthData.auto_prediction.trigger_threshold}
      <br />
      Predicted Maintenance: {
        healthData.auto_prediction.prediction_result.prediction_formatted
      }
      <br />
      <strong>Action Required: Schedule immediate maintenance!</strong>
    </Alert>
  );
}
```

## 📚 References

- **Health Service**: `Backend/src/services/health_service.py`
- **Prediction Service**: `Backend/src/services/prediction_service.py`
- **Health Controller**: `Backend/src/controllers/health_controller.py`
- **Configuration**: `Backend/config.py`

## 🎓 Kesimpulan

Fitur Auto-Prediction Trigger mengubah sistem dari **reactive** (menunggu tombol diklik) menjadi **proactive** (otomatis mendeteksi dan memprediksi). Ini meningkatkan efektivitas predictive maintenance dan mengurangi risiko downtime tidak terencana.

---

**Version**: 1.0  
**Last Updated**: October 22, 2025  
**Author**: Backend Development Team

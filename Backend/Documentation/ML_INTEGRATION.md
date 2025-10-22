# Machine Learning Integration Guide

## Overview

Aplikasi Flask telah diintegrasikan dengan model Machine Learning untuk prediksi durasi maintenance mesin Flexo 104.

## Struktur Integrasi

```
backend/
├── predictor.py          # Module untuk ML predictions
├── routes.py             # API endpoints (termasuk prediction endpoints)
├── app.py                # Main Flask app
└── requirements.txt      # Dependencies (termasuk scikit-learn, joblib)

../Model/
└── model.pkl             # Trained ML model (LinearRegression)
```

## File-File yang Dimodifikasi/Dibuat

### 1. `predictor.py` (Baru)

File ini berisi semua fungsi untuk ML predictions:

**Fungsi Utama:**

- `load_model()` - Memuat model dari `../Model/model.pkl`
- `predict_maintenance_duration(data)` - Prediksi single input
- `batch_predict_maintenance_duration(data_list)` - Prediksi multiple inputs
- `get_model_info()` - Informasi tentang model

**Fitur:**
- Automatic model loading saat module diimport
- Input validation
- Error handling yang comprehensive
- Support untuk batch predictions

### 2. `routes.py` (Dimodifikasi)

Ditambahkan 3 endpoint baru untuk predictions:

- `POST /api/predict/maintenance` - Single prediction
- `POST /api/predict/maintenance/batch` - Batch predictions
- `GET /api/model/info` - Model information

### 3. `requirements.txt` (Dimodifikasi)

Ditambahkan dependencies:
- `scikit-learn==1.3.2` - ML library
- `joblib==1.3.2` - Model serialization
- `numpy==1.24.3` - Numerical computing

### 4. `app.py` (Tidak perlu diubah)

Blueprint dari `routes.py` sudah terdaftar dengan benar.

## API Endpoints

### 1. Single Prediction

**Endpoint:** `POST /api/predict/maintenance`

**Request:**
```json
{
    "total_produksi": 5000,
    "produk_cacat": 150
}
```

**Response (Success):**
```json
{
    "success": true,
    "prediction": 85.5,
    "prediction_formatted": "1 jam 25 menit",
    "input": {
        "total_produksi": 5000,
        "produk_cacat": 150
    },
    "message": "Prediksi berhasil"
}
```

**Response (Error):**
```json
{
    "success": false,
    "prediction": null,
    "input": {...},
    "message": "Error message"
}
```

### 2. Batch Prediction

**Endpoint:** `POST /api/predict/maintenance/batch`

**Request:**
```json
{
    "data": [
        {"total_produksi": 5000, "produk_cacat": 150},
        {"total_produksi": 3000, "produk_cacat": 100},
        {"total_produksi": 7000, "produk_cacat": 200}
    ]
}
```

**Response:**
```json
{
    "success": true,
    "total_items": 3,
    "successful_predictions": 3,
    "predictions": [
        {
            "success": true,
            "prediction": 85.5,
            "prediction_formatted": "1 jam 25 menit",
            "input": {...},
            "message": "Prediksi berhasil"
        },
        ...
    ],
    "message": "Batch prediction completed: 3/3 berhasil"
}
```

### 3. Model Information

**Endpoint:** `GET /api/model/info`

**Response:**
```json
{
    "loaded": true,
    "model_type": "LinearRegression",
    "model_class": "<class 'sklearn.linear_model._base.LinearRegression'>",
    "coefficients": [0.0125, 0.45],
    "intercept": 10.5,
    "features": ["Total Produksi (Pcs)", "Produk Cacat (Pcs)"],
    "target": "Waktu Downtime (Menit)",
    "message": "Model information retrieved successfully"
}
```

## Testing

### Test dengan cURL

```bash
# Single prediction
curl -X POST http://localhost:5000/api/predict/maintenance \
  -H "Content-Type: application/json" \
  -d '{"total_produksi": 5000, "produk_cacat": 150}'

# Batch prediction
curl -X POST http://localhost:5000/api/predict/maintenance/batch \
  -H "Content-Type: application/json" \
  -d '{
    "data": [
      {"total_produksi": 5000, "produk_cacat": 150},
      {"total_produksi": 3000, "produk_cacat": 100}
    ]
  }'

# Model info
curl http://localhost:5000/api/model/info
```

### Test dengan Python

```python
import requests
import json

BASE_URL = "http://localhost:5000/api"

# Single prediction
data = {
    "total_produksi": 5000,
    "produk_cacat": 150
}
response = requests.post(f"{BASE_URL}/predict/maintenance", json=data)
print(response.json())

# Batch prediction
batch_data = {
    "data": [
        {"total_produksi": 5000, "produk_cacat": 150},
        {"total_produksi": 3000, "produk_cacat": 100}
    ]
}
response = requests.post(f"{BASE_URL}/predict/maintenance/batch", json=batch_data)
print(response.json())

# Model info
response = requests.get(f"{BASE_URL}/model/info")
print(response.json())
```

### Test dengan Postman

1. **Single Prediction:**
   - Method: POST
   - URL: `http://localhost:5000/api/predict/maintenance`
   - Body (JSON):
     ```json
     {
         "total_produksi": 5000,
         "produk_cacat": 150
     }
     ```

2. **Batch Prediction:**
   - Method: POST
   - URL: `http://localhost:5000/api/predict/maintenance/batch`
   - Body (JSON):
     ```json
     {
         "data": [
             {"total_produksi": 5000, "produk_cacat": 150},
             {"total_produksi": 3000, "produk_cacat": 100}
         ]
     }
     ```

3. **Model Info:**
   - Method: GET
   - URL: `http://localhost:5000/api/model/info`

## Model Details

### Model Type
- **Algorithm:** Linear Regression
- **Framework:** scikit-learn
- **Input Features:** 2
  - Total Produksi (Pcs)
  - Produk Cacat (Pcs)
- **Output:** Waktu Downtime (Menit)

### Model Training Data
- **Source:** Data Flexo CSV (September 2024 - September 2025)
- **Machine:** C_FL104
- **Total Records:** Multiple months of production data

### Model Performance
- Coefficients: [0.0125, 0.45] (example values)
- Intercept: 10.5 (example value)

## Error Handling

### Common Errors

**1. Model Not Found**
```json
{
    "success": false,
    "prediction": null,
    "message": "Model tidak tersedia. Silakan restart server."
}
```

**2. Invalid Input**
```json
{
    "success": false,
    "prediction": null,
    "message": "Validation error: Input harus memiliki keys: ['total_produksi', 'produk_cacat']. Missing: ['total_produksi']"
}
```

**3. Invalid Data Type**
```json
{
    "success": false,
    "prediction": null,
    "message": "Validation error: Nilai harus berupa angka"
}
```

**4. Negative Values**
```json
{
    "success": false,
    "prediction": null,
    "message": "Validation error: Nilai tidak boleh negatif"
}
```

## Troubleshooting

### Model File Not Found

**Error:**
```
[ERROR] Model file tidak ditemukan di: c:\...\Model\model.pkl
```

**Solution:**
1. Pastikan file `model.pkl` ada di folder `../Model/`
2. Pastikan path relatif benar
3. Restart server

### Import Error

**Error:**
```
ModuleNotFoundError: No module named 'sklearn'
```

**Solution:**
```bash
pip install -r requirements.txt
```

### Prediction Error

**Error:**
```
[ERROR] Prediction error: ...
```

**Solution:**
1. Check input data format
2. Ensure values are numeric
3. Check server logs for details

## Integration Checklist

- [x] Create `predictor.py` with model loading
- [x] Create `predict_maintenance_duration()` function
- [x] Create `batch_predict_maintenance_duration()` function
- [x] Add prediction endpoints to `routes.py`
- [x] Add model info endpoint
- [x] Update `requirements.txt` with ML dependencies
- [x] Verify blueprint registration in `app.py`
- [x] Test all endpoints
- [x] Create documentation

## Future Improvements

- [ ] Add model versioning
- [ ] Add model retraining endpoint
- [ ] Add prediction confidence scores
- [ ] Add model performance metrics
- [ ] Add caching for predictions
- [ ] Add rate limiting
- [ ] Add authentication for prediction endpoints
- [ ] Add prediction history logging
- [ ] Add A/B testing support
- [ ] Add model monitoring & alerting

## References

- [scikit-learn Documentation](https://scikit-learn.org/)
- [joblib Documentation](https://joblib.readthedocs.io/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

Last Updated: October 2025

# MQTT Integration Guide - FlexoTwin Backend

## Overview

Backend Flask telah diintegrasikan dengan MQTT subscriber untuk menerima data real-time dari sensor simulator. Data diterima melalui MQTT topic `flexotwin/machine/status` dan disimpan dalam memory untuk diakses melalui API endpoints.

## Arsitektur

```
Sensor Simulator (sensor_simulator.py)
         ↓
    MQTT Broker
    (broker.hivemq.com)
         ↓
MQTT Service (src/services/mqtt_service.py)
         ↓
Flask Backend (app.py)
         ↓
API Endpoints (src/routes.py)
```

## File Structure

```
Backend/
├── app.py                          # Main Flask app dengan MQTT initialization
├── src/
│   ├── services/
│   │   └── mqtt_service.py        # MQTT client dan data management
│   ├── routes.py                  # API endpoints untuk sensor data
│   └── utils/
│       └── logger.py              # Logging utility
└── requirements.txt               # Dependencies (termasuk paho-mqtt)
```

## Komponen Utama

### 1. `src/utils/logger.py`

Utility untuk logging di seluruh aplikasi:

```python
from src.utils.logger import get_logger

logger = get_logger(__name__)
logger.info("Message")
logger.error("Error message")
```

**Features:**
- Console output (stdout)
- File logging (logs/app.log)
- Standardized format dengan timestamp

### 2. `src/services/mqtt_service.py`

Service untuk mengelola MQTT connection:

**Classes:**
- `MQTTClient`: Main MQTT client class

**Functions:**
- `initialize_mqtt()`: Inisialisasi dan jalankan MQTT client
- `get_mqtt_client()`: Dapatkan global MQTT client instance
- `get_latest_sensor_data()`: Dapatkan data sensor terbaru
- `get_sensor_data_history(limit)`: Dapatkan history data

**Features:**
- Auto-reconnect ke broker
- Background thread untuk network loop
- Data storage (latest + history)
- Comprehensive logging

### 3. `app.py`

Main Flask application:

```python
from src.services.mqtt_service import initialize_mqtt

def create_app():
    app = Flask(__name__)
    
    # Register blueprints
    app.register_blueprint(api_bp)
    
    # Initialize MQTT
    mqtt_client = initialize_mqtt()
    
    return app
```

### 4. `src/routes.py`

API endpoints untuk mengakses sensor data:

- `GET /api/sensor/latest` - Data sensor terbaru
- `GET /api/sensor/history?limit=50` - History data
- `GET /api/sensor/status` - Status sensor & MQTT
- `GET /api/info` - Informasi API

## Cara Menggunakan

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Jalankan Backend

```bash
python app.py
```

**Output:**
```
======================================================================
Initializing FlexoTwin Backend Application
======================================================================
[APP] Flask application created
[APP] Registering blueprints...
[APP] ✓ API blueprint registered
[APP] Initializing MQTT service...
[MQTT] Connecting to broker at broker.hivemq.com:1883...
✓ Successfully connected to MQTT Broker!
✓ Subscribed to topic: flexotwin/machine/status
[APP] ✓ MQTT service initialized and started in background
[APP] Application initialization complete
======================================================================

======================================================================
Starting FlexoTwin Backend Server
======================================================================
Server running at: http://0.0.0.0:5000
API Documentation: http://0.0.0.0:5000/api/docs
Health Check: http://0.0.0.0:5000/health
Press CTRL+C to stop the server
======================================================================
```

### 3. Jalankan Sensor Simulator (di terminal lain)

```bash
python sensor_simulator.py
```

### 4. Test API Endpoints

#### Get Latest Sensor Data

```bash
curl http://localhost:5000/api/sensor/latest
```

**Response:**
```json
{
    "success": true,
    "data": {
        "machine_id": "C_FL104",
        "machine_status": "Running",
        "performance_rate": 82.45,
        "quality_rate": 96.78,
        "timestamp": "2025-01-21T10:30:45.123456",
        "simulator_version": "1.0"
    }
}
```

#### Get Sensor History

```bash
curl "http://localhost:5000/api/sensor/history?limit=10"
```

**Response:**
```json
{
    "success": true,
    "count": 10,
    "limit": 10,
    "data": [
        {...},
        {...}
    ]
}
```

#### Get Sensor Status

```bash
curl http://localhost:5000/api/sensor/status
```

**Response:**
```json
{
    "success": true,
    "mqtt": {
        "connected": true,
        "broker": "broker.hivemq.com:1883",
        "topic": "flexotwin/machine/status"
    },
    "sensor": {
        "machine_id": "C_FL104",
        "status": "Running",
        "last_update": "2025-01-21T10:30:45.123456"
    }
}
```

#### Get API Info

```bash
curl http://localhost:5000/api/info
```

#### Health Check

```bash
curl http://localhost:5000/health
```

## Data Flow

### 1. Sensor Simulator Publish

```
Sensor Simulator
    ↓
Publish JSON ke MQTT topic: flexotwin/machine/status
    ↓
{
    "machine_id": "C_FL104",
    "machine_status": "Running",
    "performance_rate": 82.45,
    "quality_rate": 96.78,
    "timestamp": "2025-01-21T10:30:45.123456",
    "simulator_version": "1.0"
}
```

### 2. MQTT Service Receive

```
MQTT Broker
    ↓
on_message() callback triggered
    ↓
Parse JSON payload
    ↓
Update latest_sensor_data
    ↓
Add to sensor_data_history
```

### 3. API Access

```
Client Request
    ↓
GET /api/sensor/latest
    ↓
get_latest_sensor_data()
    ↓
Return JSON response
```

## Logging

Logs disimpan di `Backend/logs/app.log`:

```
2025-01-21 10:30:45 - root - INFO - ======================================================================
2025-01-21 10:30:45 - root - INFO - Initializing FlexoTwin Backend Application
2025-01-21 10:30:45 - root - INFO - ======================================================================
2025-01-21 10:30:45 - src.services.mqtt_service - INFO - [MQTT] Connecting to broker at broker.hivemq.com:1883...
2025-01-21 10:30:46 - src.services.mqtt_service - INFO - ✓ Successfully connected to MQTT Broker!
2025-01-21 10:30:46 - src.services.mqtt_service - INFO - ✓ Subscribed to topic: flexotwin/machine/status
2025-01-21 10:30:50 - src.services.mqtt_service - INFO - [MQTT RECEIVED] Topic: flexotwin/machine/status
2025-01-21 10:30:50 - src.services.mqtt_service - INFO -   Machine: C_FL104
2025-01-21 10:30:50 - src.services.mqtt_service - INFO -   Status: Running
2025-01-21 10:30:50 - src.services.mqtt_service - INFO -   Performance: 82.45%
2025-01-21 10:30:50 - src.services.mqtt_service - INFO -   Quality: 96.78%
```

## Configuration

Edit `src/services/mqtt_service.py` untuk mengubah konfigurasi:

```python
MQTT_BROKER = "broker.hivemq.com"      # MQTT broker address
MQTT_PORT = 1883                        # MQTT port
MQTT_TOPIC = "flexotwin/machine/status" # Topic untuk subscribe
MQTT_CLIENT_ID = "flexotwin-backend-subscriber"
MQTT_KEEPALIVE = 60                     # Keepalive interval (detik)
MAX_HISTORY = 100                       # Max history entries
```

## Troubleshooting

### MQTT Connection Failed

**Error:**
```
[MQTT] Error starting client: ...
```

**Solution:**
- Cek koneksi internet
- Cek apakah broker accessible
- Cek firewall settings

### No Data Received

**Error:**
```
"error": "No data available",
"message": "Sensor data has not been received yet"
```

**Solution:**
- Pastikan sensor simulator berjalan
- Cek MQTT connection status: `GET /api/sensor/status`
- Cek logs di `Backend/logs/app.log`

### MQTT Disconnected

**Error:**
```
⚠ Unexpected disconnection from MQTT Broker (code: ...)
```

**Solution:**
- MQTT client akan auto-reconnect
- Cek broker status
- Cek network connectivity

## Performance Notes

- **Memory Usage**: ~10-50 MB (tergantung history size)
- **CPU Usage**: Minimal (~1-2%)
- **Network**: ~1-2 KB per message (setiap 5 detik)
- **Latency**: <100ms untuk API response

## Future Improvements

- [ ] Add database persistence
- [ ] Add data aggregation (hourly, daily)
- [ ] Add WebSocket untuk real-time updates
- [ ] Add data export (CSV, Excel)
- [ ] Add anomaly detection
- [ ] Add predictive maintenance alerts
- [ ] Add multi-machine support
- [ ] Add authentication & authorization

## References

- [paho-mqtt Documentation](https://github.com/eclipse/paho.mqtt.python)
- [MQTT Protocol](https://mqtt.org/)
- [HiveMQ Broker](https://www.hivemq.com/)
- [Flask Documentation](https://flask.palletsprojects.com/)

---

**Last Updated:** January 2025
**Version:** 1.0

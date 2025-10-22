# FlexoTwin Smart Sensor Simulator - User Guide

## Overview

`sensor_simulator.py` adalah simulator sensor cerdas yang meniru perilaku mesin Flexo 104 berdasarkan data historis selama 1 tahun. Simulator ini membaca statistik dari data CSV dan mempublikasikan data sensor simulasi ke MQTT broker.

## Fitur Utama

✅ **Data-Driven Simulation** - Berbasis statistik dari data historis
✅ **MQTT Integration** - Publish ke broker publik HiveMQ
✅ **Smart Downtime Simulation** - Probabilitas downtime dari data real
✅ **Performance Variance** - Simulasi performa ±5% dari rata-rata
✅ **Quality Variance** - Simulasi kualitas ±2% dari rata-rata
✅ **Real-time Logging** - Console output untuk monitoring

## Instalasi

### 1. Install Dependencies

```bash
pip install pandas paho-mqtt
```

Atau gunakan requirements.txt:
```bash
pip install -r requirements.txt
```

### 2. Verifikasi Data

Pastikan folder `Data Flexo CSV/` ada dan berisi file CSV dengan kolom:
- `Availability Rate (%)`
- `Performance Rate (%)`
- `Quality Rate (%)`

## Cara Menjalankan

### Basic Usage

```bash
python sensor_simulator.py
```

### Output Contoh

```
======================================================================
FlexoTwin Smart Sensor Simulator
Machine: Flexo 104
======================================================================

======================================================================
PHASE 1: DATA ANALYSIS & INITIALIZATION
======================================================================

[INFO] Membaca data dari folder: c:\...\Data Flexo CSV
[INFO] Ditemukan 13 file CSV
[INFO] Membaca dan menggabungkan file CSV...
  ✓ Laporan Flexo Januari 2025.csv (1500 baris)
  ✓ Laporan Flexo Februari 2025.csv (1400 baris)
  ...

[SUCCESS] Total data gabungan: 18500 baris

[INFO] Menghitung statistik dari data historis...
  ✓ Availability Rate: 85.32%
  ✓ Performance Rate: 82.15%
  ✓ Quality Rate: 96.45%

[STATISTICS]
  • Average Availability Rate: 85.32%
  • Average Performance Rate: 82.15%
  • Average Quality Rate: 96.45%
  • Downtime Probability: 0.1468 (14.68%)

======================================================================
PHASE 2: MQTT CONNECTION & SIMULATION
======================================================================

[INFO] Menghubungkan ke MQTT broker: broker.hivemq.com:1883

[SUCCESS] Terhubung ke MQTT broker: broker.hivemq.com

[INFO] Simulasi dimulai. Interval: 5 detik
[INFO] Topic MQTT: flexotwin/machine/status
[INFO] Tekan CTRL+C untuk menghentikan simulasi

======================================================================
SIMULATION RUNNING
======================================================================

✓ [2025-01-21T10:30:45.123456] Status: Running   | Performance: 81.23% | Quality: 96.78%
✓ [2025-01-21T10:30:50.234567] Status: Running   | Performance: 83.45% | Quality: 95.92%
⚠ [2025-01-21T10:30:55.345678] Status: Downtime | Performance:  0.00% | Quality:  0.00%
✓ [2025-01-21T10:31:00.456789] Status: Running   | Performance: 82.10% | Quality: 96.34%
```

## Konfigurasi

Edit variabel di bagian `KONFIGURASI` untuk customize:

```python
# Path ke folder data
DATA_FOLDER = Path(__file__).parent / "Data Flexo CSV"

# MQTT Configuration
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "flexotwin/machine/status"

# Simulation Configuration
SIMULATION_INTERVAL = 5  # Detik
PERFORMANCE_VARIANCE = 5  # ±5%
QUALITY_VARIANCE = 2     # ±2%
```

## MQTT Topic & Payload

### Topic
```
flexotwin/machine/status
```

### Payload Format (JSON)
```json
{
    "machine_id": "C_FL104",
    "machine_status": "Running",
    "performance_rate": 82.45,
    "quality_rate": 96.78,
    "timestamp": "2025-01-21T10:30:45.123456",
    "simulator_version": "1.0"
}
```

### Payload Contoh (Downtime)
```json
{
    "machine_id": "C_FL104",
    "machine_status": "Downtime",
    "performance_rate": 0.0,
    "quality_rate": 0.0,
    "timestamp": "2025-01-21T10:30:55.345678",
    "simulator_version": "1.0"
}
```

## Monitoring MQTT Data

### Menggunakan MQTT Explorer

1. Download [MQTT Explorer](http://mqtt-explorer.com/)
2. Connect ke `broker.hivemq.com:1883`
3. Subscribe ke topic `flexotwin/machine/status`
4. Lihat data real-time

### Menggunakan Python

```python
import paho.mqtt.client as mqtt
import json

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    print(f"Status: {data['machine_status']}")
    print(f"Performance: {data['performance_rate']}%")
    print(f"Quality: {data['quality_rate']}%")

client = mqtt.Client()
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
client.subscribe("flexotwin/machine/status")
client.loop_forever()
```

### Menggunakan mosquitto_sub (CLI)

```bash
mosquitto_sub -h broker.hivemq.com -t "flexotwin/machine/status"
```

## Statistik yang Digunakan

### Availability Rate
- **Definisi**: Persentase waktu mesin beroperasi
- **Penggunaan**: Menghitung probabilitas downtime
- **Formula**: `downtime_probability = 1 - (avg_availability / 100)`

### Performance Rate
- **Definisi**: Kecepatan produksi relatif terhadap target
- **Penggunaan**: Simulasi performa dengan variance ±5%
- **Range**: 0-100%

### Quality Rate
- **Definisi**: Persentase produk yang memenuhi standar kualitas
- **Penggunaan**: Simulasi kualitas dengan variance ±2%
- **Range**: 0-100%

## Troubleshooting

### Error: "Folder tidak ditemukan"
```
[ERROR] Gagal menganalisis data: Folder tidak ditemukan: c:\...\Data Flexo CSV
```

**Solusi:**
- Pastikan folder `Data Flexo CSV` ada di direktori yang sama dengan script
- Pastikan path benar

### Error: "Tidak ada file CSV"
```
[ERROR] Gagal menganalisis data: Tidak ada file CSV di folder
```

**Solusi:**
- Pastikan ada file `.csv` di folder `Data Flexo CSV`
- Pastikan file tidak kosong

### Error: "Gagal terhubung ke MQTT broker"
```
[ERROR] Gagal setup MQTT connection: ...
```

**Solusi:**
- Cek koneksi internet
- Cek apakah broker `broker.hivemq.com` accessible
- Coba broker alternatif: `test.mosquitto.org`

### Data tidak terkirim ke MQTT
```
[WARNING] MQTT client tidak terhubung. Data tidak terkirim.
```

**Solusi:**
- Tunggu beberapa detik untuk koneksi establish
- Cek firewall settings
- Cek MQTT broker status

## Performance Notes

- **Memory Usage**: ~50-100 MB (tergantung ukuran data CSV)
- **CPU Usage**: Minimal (~1-2%)
- **Network**: ~1-2 KB per publish (setiap 5 detik)
- **Latency**: <100ms untuk publish

## Advanced Usage

### Custom MQTT Broker

Edit konfigurasi:
```python
MQTT_BROKER = "your-broker.com"
MQTT_PORT = 1883
```

### Custom Simulation Interval

```python
SIMULATION_INTERVAL = 10  # 10 detik
```

### Custom Variance

```python
PERFORMANCE_VARIANCE = 10  # ±10%
QUALITY_VARIANCE = 5       # ±5%
```

## Integration dengan Backend API

Untuk mengintegrasikan dengan Flask backend:

1. **Subscribe ke MQTT topic** di backend
2. **Store data** ke database
3. **Expose via API** untuk frontend

Contoh:
```python
# Di backend Flask
import paho.mqtt.client as mqtt

def on_message(client, userdata, msg):
    data = json.loads(msg.payload.decode())
    # Store ke database
    save_sensor_data(data)

client = mqtt.Client()
client.on_message = on_message
client.connect("broker.hivemq.com", 1883, 60)
client.subscribe("flexotwin/machine/status")
client.loop_start()
```

## Stopping the Simulator

Tekan `CTRL+C` untuk menghentikan:

```
^C

[INFO] Simulasi dihentikan oleh user
[INFO] Total iterasi: 1234
[INFO] MQTT connection closed
```

## Future Improvements

- [ ] Add database logging
- [ ] Add anomaly detection
- [ ] Add predictive maintenance alerts
- [ ] Add multiple machine simulation
- [ ] Add configurable variance per machine
- [ ] Add historical data replay
- [ ] Add REST API for control
- [ ] Add WebSocket for real-time updates

## References

- [MQTT Protocol](https://mqtt.org/)
- [HiveMQ Broker](https://www.hivemq.com/)
- [paho-mqtt Documentation](https://github.com/eclipse/paho.mqtt.python)
- [Pandas Documentation](https://pandas.pydata.org/)

---

**Last Updated:** January 2025
**Version:** 1.0

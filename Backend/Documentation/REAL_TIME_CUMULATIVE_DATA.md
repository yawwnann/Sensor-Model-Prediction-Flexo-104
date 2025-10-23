# Real-Time Cumulative Data Integration Guide

## 📋 Overview

This document explains the implementation of **real-time cumulative production data** for the auto-prediction trigger feature. The system now uses actual production and defect counts from the sensor simulator instead of placeholder default values.

---

## 🎯 Implementation Summary

### What Changed?

**BEFORE (Placeholder Approach):**

- Auto-prediction triggered with default values: `total_produksi: 4000`, `produk_cacat: 150`
- No connection to actual machine production
- Served as basic early warning system

**AFTER (Real-Time Data Approach):**

- Auto-prediction uses **cumulative production data from simulator**
- Data flows: Sensor Simulator → MQTT → Database → Health Service
- Accurate predictions based on actual shift performance

---

## 🔄 Data Flow Architecture

```
┌─────────────────────┐
│ Sensor Simulator    │  Step 1: Generate cumulative data
│ (sensor_simulator.py)│  - cumulative_production
└──────────┬──────────┘  - cumulative_defects
           │
           │ MQTT (HiveMQ)
           │ Topic: flexotwin/machine/status
           ▼
┌─────────────────────┐
│  MQTT Service       │  Step 2: Receive & parse
│  (mqtt_service.py)  │  - Extract cumulative fields
└──────────┬──────────┘  - Log to database
           │
           │ Database Call
           ▼
┌─────────────────────┐
│  Database Service   │  Step 3: Store in PostgreSQL
│(database_service.py)│  - Save to machine_logs table
└──────────┬──────────┘  - cumulative_production (INT)
           │              - cumulative_defects (INT)
           │
           │ Query Latest
           ▼
┌─────────────────────┐
│  Health Service     │  Step 4: Use for auto-prediction
│ (health_service.py) │  - Fetch latest cumulative data
└─────────────────────┘  - Trigger prediction when health < 40
```

---

## 🛠️ Implementation Details

### Step 1: Sensor Simulator Modifications

**File:** `Sensor/sensor_simulator.py`

**Added Variables:**

```python
BASE_PRODUCTION_RATE = 100  # pcs per 5 seconds at 100% performance
SHIFT_DURATION_SECONDS = 28800  # 8 hours

cumulative_production = 0
cumulative_defects = 0
shift_start_time = None
```

**Production Calculation Logic:**

```python
# Calculate interval production based on performance
interval_production = int(BASE_PRODUCTION_RATE * (performance_rate / 100.0))
variation = random.uniform(0.9, 1.1)  # ±10% variation
interval_production = max(0, int(interval_production * variation))

# Calculate interval defects based on quality
defect_rate = (100 - quality_rate) / 100.0
interval_defects = int(interval_production * defect_rate)

# Update cumulative (only when Running)
cumulative_production += interval_production
cumulative_defects += interval_defects
```

**Shift Reset:**

- Automatically resets every 8 hours
- Displays shift summary before reset

**MQTT Payload Enhancement:**

```json
{
  "machine_id": "C_FL104",
  "machine_status": "Running",
  "performance_rate": 92.5,
  "quality_rate": 97.8,
  "cumulative_production": 5420, // ✅ NEW
  "cumulative_defects": 119, // ✅ NEW
  "interval_production": 95, // Reference
  "interval_defects": 2, // Reference
  "timestamp": "2025-01-15T14:30:45",
  "simulator_version": "2.0" // Updated version
}
```

---

### Step 2: Database Schema Update

**Migration File:** `Backend/migrations/add_cumulative_columns.sql`

**SQL Changes:**

```sql
ALTER TABLE machine_logs
ADD COLUMN IF NOT EXISTS cumulative_production INTEGER DEFAULT 0,
ADD COLUMN IF NOT EXISTS cumulative_defects INTEGER DEFAULT 0;

CREATE INDEX IF NOT EXISTS idx_machine_logs_timestamp_desc
ON machine_logs (timestamp DESC);

CREATE INDEX IF NOT EXISTS idx_machine_logs_cumulative
ON machine_logs (cumulative_production, cumulative_defects);
```

**Run Migration:**

```bash
cd Backend
python run_migration.py
```

**Expected Output:**

```
========================================================================
DATABASE MIGRATION: Add Cumulative Columns
========================================================================

✅ Migration successful! New columns added:
  - cumulative_production (INTEGER)
  - cumulative_defects (INTEGER)
```

---

### Step 3: Database Service Updates

**File:** `Backend/src/services/database_service.py`

**Modified `log_machine_status()`:**

```python
def log_machine_status(self, data):
    insert_sql = """
        INSERT INTO machine_logs (
            timestamp, machine_status, performance_rate, quality_rate,
            cumulative_production, cumulative_defects
        )
        VALUES (%s, %s, %s, %s, %s, %s);
    """
    # ... save cumulative_production and cumulative_defects
```

**Modified `get_latest_machine_status()`:**

```python
def get_latest_machine_status(self):
    query = """
        SELECT timestamp, machine_status, performance_rate, quality_rate,
               cumulative_production, cumulative_defects
        FROM machine_logs
        ORDER BY timestamp DESC LIMIT 1
    """
    # ... returns dict with cumulative fields
```

---

### Step 4: MQTT Service Updates

**File:** `Backend/src/services/mqtt_service.py`

**Enhanced `on_message()` Logging:**

```python
logger.info(f"[MQTT RECEIVED] Topic: {msg.topic}")
logger.info(f"  🏭 Cumulative Production: {data.get('cumulative_production', 0)} pcs")
logger.info(f"  ❌ Cumulative Defects: {data.get('cumulative_defects', 0)} pcs")
```

**Updated `latest_sensor_data` Structure:**

```python
latest_sensor_data = {
    "machine_id": None,
    "machine_status": None,
    "performance_rate": None,
    "quality_rate": None,
    "cumulative_production": 0,  // ✅ NEW
    "cumulative_defects": 0,     // ✅ NEW
    "timestamp": None,
    "simulator_version": None
}
```

---

### Step 5: Health Service Updates

**File:** `Backend/src/services/health_service.py`

**Modified Auto-Trigger Logic:**

```python
if final_health_index < CRITICAL_THRESHOLD:
    # Fetch REAL cumulative data from database
    latest_status = db_service.get_latest_machine_status()

    if latest_status and latest_status.get("cumulative_production") is not None:
        # Use real cumulative data
        total_produksi = latest_status.get("cumulative_production", 0)
        produk_cacat = latest_status.get("cumulative_defects", 0)

        logger.info(
            f"✅ Using REAL cumulative data from simulator: "
            f"Production={total_produksi} pcs, Defects={produk_cacat} pcs"
        )

        # Validation: if production = 0, use minimal values
        if total_produksi == 0:
            total_produksi = 100  # Minimal for prediction
            produk_cacat = 5
    else:
        # Fallback: use defaults if cumulative not available
        total_produksi = 4000
        produk_cacat = 150

    input_data = {
        "total_produksi": total_produksi,
        "produk_cacat": produk_cacat
    }

    prediction_result = prediction_service.predict_maintenance_duration(input_data)
```

---

## 🚀 Testing & Validation

### Step 1: Run Database Migration

```bash
cd Backend
python run_migration.py
```

**Verify:** Check that `cumulative_production` and `cumulative_defects` columns exist in `machine_logs` table.

---

### Step 2: Start Sensor Simulator

```bash
cd Sensor
python sensor_simulator.py
```

**Expected Output:**

```
========================================================================
🚀 SENSOR SIMULATOR STARTED (v2.0)
========================================================================
📍 Target Machine: C_FL104
🏭 Base Production Rate: 100 pcs / 5 sec
⏰ Shift Duration: 8.0 hours
========================================================================

🟢 [Iter #0001] Status: Running
  Performance: 92.34%
  Quality: 97.85%
  🏭 Cumulative Production: 95 pcs
  ❌ Cumulative Defects: 2 pcs
  📊 Current Defect Rate: 2.11%
  ✅ Published to flexotwin/machine/status
```

---

### Step 3: Start Backend Server

```bash
cd Backend
python app.py
```

**Check MQTT Logs:**

```
[MQTT RECEIVED] Topic: flexotwin/machine/status
  Machine: C_FL104
  Status: Running
  Performance: 92.34%
  Quality: 97.85%
  🏭 Cumulative Production: 95 pcs
  ❌ Cumulative Defects: 2 pcs

Machine status logged: Production=95, Defects=2
```

---

### Step 4: Verify Database Storage

Query the database to confirm cumulative data is being saved:

```sql
SELECT
    timestamp,
    machine_status,
    performance_rate,
    quality_rate,
    cumulative_production,
    cumulative_defects
FROM machine_logs
ORDER BY timestamp DESC
LIMIT 10;
```

---

### Step 5: Trigger Auto-Prediction

**Option A: Force Critical Health (Test)**

Modify `health_service.py` temporarily:

```python
CRITICAL_THRESHOLD = 80.0  # Force trigger for testing
```

**Option B: Wait for Real Critical Condition**

Monitor the dashboard for components with health index < 40.

**Expected Backend Logs:**

```
⚠️ CRITICAL HEALTH DETECTED! Health Index: 38.5 < 40.0
📊 Fetching real-time cumulative production data from database...
✅ Using REAL cumulative data from simulator: Production=5420 pcs, Defects=119 pcs
🤖 Auto-triggering maintenance prediction with input: {'total_produksi': 5420, 'produk_cacat': 119}
✅ AUTO-PREDICTION COMPLETED | Health Index: 38.5 | Predicted Maintenance Duration: 2 jam 15 menit
```

---

## 📊 Production Rate Calculations

### Base Production Rate

- **100 pcs per 5 seconds** at 100% performance
- **1200 pcs per minute** at 100% performance
- **72,000 pcs per hour** at 100% performance

### Performance Adjustment

```
Actual Production = BASE_RATE × (performance_rate / 100) × random_variation
```

**Example:**

- Performance: 92.5%
- Base rate: 100 pcs
- Random variation: 1.05 (5% above)
- Actual: `100 × 0.925 × 1.05 = 97 pcs`

### Defect Calculation

```
Defect Rate = (100 - quality_rate) / 100
Defects = Production × Defect_Rate
```

**Example:**

- Production: 97 pcs
- Quality: 97.8%
- Defect rate: 2.2%
- Defects: `97 × 0.022 = 2 pcs`

---

## 🔄 Shift Reset Behavior

### Automatic Reset

- **Trigger:** Every 8 hours (28,800 seconds)
- **Action:** Reset `cumulative_production` and `cumulative_defects` to 0
- **Display:** Shows shift summary before reset

**Console Output:**

```
========================================================================
🔄 SHIFT RESET
========================================================================
Previous shift summary:
  Total Production: 34,560 pcs
  Total Defects: 760 pcs
  Defect Rate: 2.20%
========================================================================
```

---

## ⚙️ Configuration Parameters

### Simulator Configuration

| Parameter                | Value   | Description                              |
| ------------------------ | ------- | ---------------------------------------- |
| `BASE_PRODUCTION_RATE`   | 100 pcs | Production per 5 sec at 100% performance |
| `SHIFT_DURATION_SECONDS` | 28800   | 8 hours in seconds                       |
| `UPDATE_INTERVAL`        | 5       | MQTT publish interval (seconds)          |

### Health Service Configuration

| Parameter            | Value | Description                             |
| -------------------- | ----- | --------------------------------------- |
| `CRITICAL_THRESHOLD` | 40.0  | Health index threshold for auto-trigger |
| `RPN_WEIGHT`         | 0.6   | RPN contribution to health index        |
| `OEE_WEIGHT`         | 0.4   | OEE contribution to health index        |

---

## 🛡️ Error Handling

### Zero Production Scenario

**Problem:** Shift just started, cumulative_production = 0

**Solution:**

```python
if total_produksi == 0:
    logger.warning("⚠️ Cumulative production is 0 (shift just started or machine idle)")
    total_produksi = 100  # Minimal for prediction
    produk_cacat = 5
```

### Database Unavailable

**Problem:** Cumulative columns not yet migrated

**Solution:**

```python
if latest_status and latest_status.get("cumulative_production") is not None:
    # Use real data
else:
    # Fallback to defaults
    total_produksi = 4000
    produk_cacat = 150
```

### MQTT Connection Lost

**Problem:** Simulator disconnected, no new data

**Solution:**

- `get_latest_machine_status()` returns last known value
- Auto-prediction uses most recent cumulative data
- Frontend shows warning if data is stale

---

## 📈 Benefits of Real-Time Data

### 1. Accuracy

- Predictions based on **actual shift performance**
- Reflects real production context
- Adapts to machine variability

### 2. Timeliness

- **Immediate response** to critical health conditions
- No waiting for manual data entry
- Continuous monitoring

### 3. Traceability

- All data logged to database
- Full audit trail
- Historical analysis possible

### 4. Scalability

- Works for multiple machines
- Extensible to more data points
- Future-proof architecture

---

## 🔧 Troubleshooting

### Issue 1: Cumulative data not showing in database

**Check:**

1. Run migration: `python run_migration.py`
2. Verify columns exist: Query `information_schema.columns`
3. Restart backend after migration

### Issue 2: Auto-prediction using fallback defaults

**Check:**

1. Simulator is running and sending data
2. MQTT connection is established
3. Database logs show cumulative values
4. Check backend logs for "Using REAL cumulative data" message

### Issue 3: Prediction accuracy seems off

**Check:**

1. Verify production rate calculations
2. Check shift hasn't just reset (cumulative = 0)
3. Review model training data range
4. Validate defect rate calculations

---

## 📝 Next Steps

### Phase 2 Enhancements (Future)

1. **Multiple Shift Support**

   - Track shift_id in database
   - Compare performance across shifts
   - Shift-specific analytics

2. **Trend Analysis**

   - Moving average of defect rates
   - Performance degradation detection
   - Predictive maintenance scheduling

3. **Advanced Alerts**

   - Defect rate spike detection
   - Production anomaly alerts
   - Quality trend warnings

4. **Dashboard Widgets**
   - Real-time production counter
   - Shift progress bar
   - Cumulative defect chart

---

## 🎓 Summary

✅ **Completed:**

- Sensor simulator generates cumulative production data
- Database schema updated with cumulative columns
- MQTT service parses and logs cumulative data
- Health service uses real-time data for auto-prediction
- Comprehensive logging for debugging

✅ **Validated:**

- Production calculation accuracy
- Shift reset functionality
- Database storage
- Auto-prediction trigger with real data

✅ **Documented:**

- Implementation details
- Data flow architecture
- Testing procedures
- Troubleshooting guide

---

**Version:** 2.0  
**Last Updated:** 2025-01-15  
**Authors:** FlexoTwin Development Team

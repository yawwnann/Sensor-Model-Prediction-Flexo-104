# 🚀 Quick Start: Real-Time Cumulative Data System

This guide walks you through setting up and running the complete system with real-time cumulative production data.

---

## ⚡ Prerequisites

- ✅ Python 3.8+
- ✅ PostgreSQL database (Supabase)
- ✅ MQTT broker access (HiveMQ)
- ✅ Node.js (for Frontend)

---

## 📋 Setup Checklist

### Step 1: Database Migration (First Time Only)

Run the migration to add cumulative columns:

```bash
cd Backend
python run_migration.py
```

**Expected Output:**

```
========================================================================
DATABASE MIGRATION: Add Cumulative Columns
========================================================================

✅ MIGRATION COMPLETED SUCCESSFULLY

You can now:
1. Run sensor_simulator.py to send cumulative data
2. Backend will automatically log cumulative values
3. Auto-prediction will use real production data
```

---

### Step 2: Start Sensor Simulator

Open **Terminal 1:**

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

**✅ Success Indicators:**

- Simulator shows version "2.0"
- Cumulative Production and Cumulative Defects are displayed
- MQTT publish successful

---

### Step 3: Start Backend Server

Open **Terminal 2:**

```bash
cd Backend
python app.py
```

**Expected Output:**

```
========================================================================
🚀 FlexoTwin Backend Server Starting...
========================================================================
✓ Database connection test passed!
✓ MQTT Client initialized
[MQTT] Connecting to broker at broker.hivemq.com:1883...
✓ Successfully connected to MQTT Broker!
✓ Subscribed to topic: flexotwin/machine/status

[MQTT RECEIVED] Topic: flexotwin/machine/status
  Machine: C_FL104
  Status: Running
  Performance: 92.34%
  Quality: 97.85%
  🏭 Cumulative Production: 95 pcs
  ❌ Cumulative Defects: 2 pcs

Machine status logged: Production=95, Defects=2

 * Running on http://127.0.0.1:5000
```

**✅ Success Indicators:**

- MQTT connection established
- Receiving data with cumulative fields (🏭 and ❌ icons)
- "Machine status logged: Production=X, Defects=Y" message

---

### Step 4: Start Frontend (Optional)

Open **Terminal 3:**

```bash
cd Frontend
npm run dev
```

**Expected Output:**

```
  VITE v5.x.x  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

Open browser: `http://localhost:5173`

---

## 🧪 Verify System is Working

### Test 1: Check Database

Run this SQL query:

```sql
SELECT
    timestamp,
    machine_status,
    cumulative_production,
    cumulative_defects
FROM machine_logs
ORDER BY timestamp DESC
LIMIT 5;
```

**Expected Result:**

```
| timestamp           | machine_status | cumulative_production | cumulative_defects |
|---------------------|----------------|-----------------------|--------------------|
| 2025-01-15 14:30:45 | Running        | 5420                  | 119                |
| 2025-01-15 14:30:40 | Running        | 5325                  | 117                |
| 2025-01-15 14:30:35 | Running        | 5230                  | 115                |
```

✅ **If you see cumulative values:** System is working correctly!

❌ **If columns are NULL or 0:** Check that simulator is running with version 2.0

---

### Test 2: Force Auto-Prediction Trigger

**Option A: Temporary Threshold Adjustment**

Edit `Backend/src/services/health_service.py`:

```python
# Line 15: Temporarily lower threshold for testing
CRITICAL_THRESHOLD = 80.0  # Force trigger (default: 40.0)
```

Restart backend and check for component health < 80.

**Option B: Wait for Real Critical Condition**

Monitor dashboard for components naturally dropping below 40.

---

### Test 3: Verify Auto-Prediction Uses Real Data

**Look for this in Backend logs:**

```
⚠️ CRITICAL HEALTH DETECTED! Health Index: 38.5 < 40.0
📊 Fetching real-time cumulative production data from database...
✅ Using REAL cumulative data from simulator: Production=5420 pcs, Defects=119 pcs
🤖 Auto-triggering maintenance prediction with input: {'total_produksi': 5420, 'produk_cacat': 119}
✅ AUTO-PREDICTION COMPLETED | Predicted Maintenance Duration: 2 jam 15 menit
```

**Key Indicators:**

- ✅ "Using REAL cumulative data"
- ✅ Production and Defects match database values
- ✅ NOT using fallback defaults (4000/150)

---

## 🔍 Monitoring Production Data

### Real-Time Console Monitoring

**Simulator Terminal:**

```
🟢 [Iter #0157] Status: Running
  Performance: 94.12%
  Quality: 98.03%
  🏭 Cumulative Production: 14,825 pcs
  ❌ Cumulative Defects: 292 pcs
  📊 Current Defect Rate: 1.97%
```

**Backend Terminal:**

```
[MQTT RECEIVED] Topic: flexotwin/machine/status
  🏭 Cumulative Production: 14,825 pcs
  ❌ Cumulative Defects: 292 pcs

Machine status logged: Production=14825, Defects=292
Latest machine status: Status=Running, Production=14825, Defects=292
```

---

### Expected Production Rates

| Time Running    | Expected Cumulative Production (at ~92% avg performance) |
| --------------- | -------------------------------------------------------- |
| 5 minutes       | ~600 pcs                                                 |
| 15 minutes      | ~1,800 pcs                                               |
| 1 hour          | ~6,600 pcs                                               |
| 4 hours         | ~26,000 pcs                                              |
| 8 hours (shift) | ~53,000 pcs                                              |

**Note:** Actual values vary based on performance rate and downtime events.

---

## 🔄 Shift Reset Behavior

Every **8 hours**, the simulator automatically resets:

```
========================================================================
🔄 SHIFT RESET
========================================================================
Previous shift summary:
  Total Production: 52,340 pcs
  Total Defects: 1,151 pcs
  Defect Rate: 2.20%
========================================================================
```

After reset:

- `cumulative_production` → 0
- `cumulative_defects` → 0
- New shift begins

---

## 🐛 Troubleshooting

### Problem: "Cumulative data not available in database"

**Symptoms:**

```
⚠️ Cumulative data not available in database. Using fallback defaults.
```

**Solutions:**

1. **Run Migration:**

   ```bash
   cd Backend
   python run_migration.py
   ```

2. **Verify Simulator Version:**

   - Check console shows "v2.0"
   - Check payload includes cumulative fields

3. **Restart Backend:**
   - Stop backend (Ctrl+C)
   - Start again: `python app.py`

---

### Problem: Production value is always 0

**Symptoms:**

- Database shows `cumulative_production = 0`
- Simulator shows production > 0

**Solutions:**

1. **Check Machine Status:**

   - Ensure machine_status = "Running"
   - Downtime = 0 production

2. **Check MQTT Connection:**

   - Backend logs show "MQTT RECEIVED"
   - Check topic matches: `flexotwin/machine/status`

3. **Check Database Logging:**
   - Backend logs show "Machine status logged"
   - No database errors

---

### Problem: Auto-prediction not triggering

**Symptoms:**

- Health index < 40 but no prediction

**Solutions:**

1. **Check Threshold:**

   ```python
   # health_service.py line 15
   CRITICAL_THRESHOLD = 40.0  # Verify this value
   ```

2. **Check Model File:**

   - Ensure `Model/model.pkl` exists
   - No errors in PredictionService

3. **Check Logs:**
   - Look for "CRITICAL HEALTH DETECTED"
   - Check for exception messages

---

## 📊 System Health Checklist

Use this checklist to verify everything is working:

### ✅ Simulator

- [ ] Shows version "2.0"
- [ ] Cumulative Production increasing
- [ ] Cumulative Defects increasing
- [ ] MQTT publish successful
- [ ] No connection errors

### ✅ Backend

- [ ] MQTT connection established
- [ ] Receiving data with cumulative fields
- [ ] Database logging successful
- [ ] No database errors
- [ ] Health calculation working

### ✅ Database

- [ ] `cumulative_production` column exists
- [ ] `cumulative_defects` column exists
- [ ] Values are being saved
- [ ] Values match simulator output

### ✅ Auto-Prediction

- [ ] Triggers when health < 40
- [ ] Uses REAL cumulative data
- [ ] Logs show production/defect values
- [ ] Prediction completes successfully

---

## 🎯 Testing Scenarios

### Scenario 1: Normal Operation

1. Start all services
2. Let simulator run for 10 minutes
3. Check cumulative values increasing steadily
4. Verify database storage

**Expected Result:** Smooth data flow, no errors

---

### Scenario 2: Downtime Event

1. Wait for simulator to randomly enter Downtime
2. Observe production stops (0 pcs interval)
3. Cumulative values stay constant during downtime
4. Production resumes when status returns to Running

**Expected Result:** Cumulative doesn't increase during downtime

---

### Scenario 3: Critical Health Auto-Trigger

1. Lower threshold to force trigger: `CRITICAL_THRESHOLD = 80.0`
2. Restart backend
3. Wait for component health < 80
4. Verify auto-prediction uses real cumulative data

**Expected Result:** Prediction with actual production values

---

### Scenario 4: Shift Reset

1. Set short shift duration for testing: `SHIFT_DURATION_SECONDS = 300` (5 min)
2. Let simulator run > 5 minutes
3. Observe shift reset message
4. Cumulative values reset to 0

**Expected Result:** Clean shift transition

---

## 🔧 Configuration Quick Reference

### Simulator (`sensor_simulator.py`)

```python
BASE_PRODUCTION_RATE = 100          # pcs per 5 sec at 100% perf
SHIFT_DURATION_SECONDS = 28800      # 8 hours
SIMULATION_INTERVAL = 5             # MQTT publish interval
```

### Health Service (`health_service.py`)

```python
CRITICAL_THRESHOLD = 40.0           # Auto-trigger threshold
RPN_WEIGHT = 0.6                    # RPN contribution
OEE_WEIGHT = 0.4                    # OEE contribution
```

### Database (`config.py`)

```python
DATABASE_URL = "postgresql://..."   # Supabase connection
DB_CONNECTION_TIMEOUT = 10
DB_RETRY_ATTEMPTS = 3
```

---

## 📚 Additional Resources

- **Full Documentation:** `Backend/Documentation/REAL_TIME_CUMULATIVE_DATA.md`
- **Auto-Prediction Guide:** `Backend/Documentation/AUTO_PREDICTION_TRIGGER.md`
- **MQTT Integration:** `Backend/Documentation/MQTT_INTEGRATION.md`
- **Troubleshooting:** `Backend/Documentation/TROUBLESHOOTING.md`

---

## 🎉 Success Criteria

Your system is fully operational when you see:

1. ✅ Simulator sending data every 5 seconds
2. ✅ Backend receiving and logging cumulative data
3. ✅ Database storing cumulative values correctly
4. ✅ Auto-prediction using REAL production data
5. ✅ Frontend displaying auto-prediction alerts

---

**Happy Monitoring! 🚀**

If you encounter issues not covered here, check the full documentation or review the backend logs for detailed error messages.

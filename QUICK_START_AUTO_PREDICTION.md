# 🚀 Quick Start: Testing Auto-Prediction Integration

## Step-by-Step Testing Guide

### 1️⃣ Start Backend Server

```bash
cd Backend
python app.py
```

**Expected Output:**

```
✓ Server dimulai...
✓ Database: PostgreSQL (Supabase)
✓ Akses API di: http://0.0.0.0:5000
```

---

### 2️⃣ Start Frontend Development Server

```bash
cd Frontend
npm run dev
```

**Expected Output:**

```
  VITE v5.x.x  ready in xxx ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.x.x:5173/
```

---

### 3️⃣ Open Dashboard

Open browser: **http://localhost:5173**

You should see:

- ✅ 5 component cards
- ✅ OEE Chart
- ✅ Trend Chart
- ✅ Prediction Panel
- ✅ FMEA Table

---

### 4️⃣ Trigger Auto-Prediction (Temporary Method)

#### Option A: Lower Threshold (Recommended for Testing)

**Edit:** `Backend/src/services/health_service.py`

```python
# Change from:
CRITICAL_THRESHOLD = 40.0

# To:
CRITICAL_THRESHOLD = 80.0  # Easier to trigger for testing
```

**Restart Backend:**

```bash
# Press Ctrl+C to stop
# Then restart:
python app.py
```

#### Option B: Wait for Real Critical Condition

Monitor dashboard until health index naturally drops below 40.

---

### 5️⃣ Observe Auto-Prediction in Action

#### On Component Card:

Look for:

- 🏷️ **Orange badge** "AUTO-PREDICTED" (top-right corner, pulsing)
- 📦 **Orange info box** with:
  - "🤖 AUTO-PREDICTION TRIGGERED"
  - "🕐 X jam X menit"
  - "⚠️ Critical health detected"

#### On Global Banner:

Look for:

- 🚨 **Large alert banner** (top of page, below header)
- **Component name** and health index
- **Predicted maintenance duration**
- **Trigger threshold information**
- **Input data** used for prediction
- **Dismiss button** (X) in top-right

---

### 6️⃣ Test Features

#### Test 1: Visual Indicators

- [ ] Badge appears with pulse animation
- [ ] Info box shows in card
- [ ] Global banner slides down smoothly
- [ ] All icons display correctly

#### Test 2: Data Accuracy

- [ ] Health index matches card and banner
- [ ] Prediction duration displayed correctly
- [ ] Threshold value shown correctly
- [ ] Input data (produksi/cacat) visible

#### Test 3: Interactivity

- [ ] Dismiss button works
- [ ] Alert disappears on dismiss
- [ ] Alert reappears on new trigger
- [ ] Auto-refresh updates data (every 5s)

#### Test 4: Multiple Components

- [ ] Multiple badges if multiple components critical
- [ ] Global banner shows all triggered components
- [ ] Each component has own card in banner

---

### 7️⃣ Monitor Backend Logs

**Open new terminal:**

```bash
cd Backend
tail -f logs/app.log | grep "AUTO"
```

**Look for:**

```
⚠️ CRITICAL HEALTH DETECTED! Health Index: 35.2 < 40.0
🤖 Auto-triggering maintenance prediction with input: {...}
✅ AUTO-PREDICTION COMPLETED | Health Index: 35.2 | Predicted: 2 jam 7 menit
```

---

### 8️⃣ Test API Directly (Optional)

```bash
# Test health endpoint
curl http://localhost:5000/api/health/Printing

# Expected response with auto_prediction field:
{
  "component_name": "Printing",
  "health_index": 35.2,
  "status": "Critical",
  "auto_prediction": {
    "triggered": true,
    "trigger_threshold": 40.0,
    "prediction_result": {
      "success": true,
      "prediction": 127.5,
      "prediction_formatted": "2 jam 7 menit"
    }
  }
}
```

---

### 9️⃣ Browser DevTools (Optional)

**Open DevTools (F12):**

#### Console:

Check for:

- API request logs: `[API Request] GET /health/...`
- API response logs: `[API Response] 200 /health/...`
- No errors in console

#### React DevTools:

Navigate to:

- Components → App → healthData
- Look for `auto_prediction` field in components

---

### 🔟 Restore Settings (After Testing)

**If you changed threshold:**

```python
# In health_service.py
CRITICAL_THRESHOLD = 40.0  # Back to default
```

**Restart backend:**

```bash
python app.py
```

---

## ✅ Success Checklist

### Backend Integration

- [x] `health_service.py` modified
- [x] `health_controller.py` updated
- [x] Threshold constant added
- [x] Logging implemented
- [x] Auto-trigger logic working
- [x] Tests passing

### Frontend Integration

- [x] `ComponentCard.jsx` shows badge
- [x] `AutoPredictionAlert.jsx` created
- [x] `App.jsx` integrates alert
- [x] `App.css` has animations
- [x] Icons imported
- [x] Responsive design
- [x] All features working

---

## 🐛 Troubleshooting

### Issue: No badge appears

**Check:**

1. Backend running? → `curl http://localhost:5000/api/health`
2. Health < threshold? → Check response
3. Frontend refreshed? → Wait 5s or manual refresh

### Issue: Global banner not showing

**Check:**

1. `AutoPredictionAlert` imported in App.jsx?
2. Component placed correctly?
3. Check browser console for errors

### Issue: Styling broken

**Check:**

1. Tailwind CSS loaded?
2. App.css imported?
3. Try: `npm run dev` (restart Vite)

### Issue: Auto-prediction not triggering

**Check:**

1. Health really < 40? (or < threshold)
2. Backend logs: `grep "AUTO"`
3. Model loaded? → `curl http://localhost:5000/api/model/info`

---

## 📸 Screenshots Expected

### Normal State

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Pre-Feeder     │  │  Feeder         │  │  Printing       │
│  Health: 75.2%  │  │  Health: 82.1%  │  │  Health: 68.5%  │
│  ✅ Sehat       │  │  ✅ Sehat       │  │  ⚠️ Perlu       │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

### Auto-Prediction Triggered

```
┌──────────────────────────────────────────────────────┐
│ 🚨 Automatic Prediction Triggered              ❌   │
│ Critical health condition detected on 1 component   │
│                                                      │
│ ┌─ Printing Unit ────────────────────────────────┐ │
│ │ 🔻 Health: 35.2%                               │ │
│ │ 🕐 Predicted Duration: 2 jam 7 menit           │ │
│ │ ⚠️ RECOMMENDATION: Schedule Immediate Maint... │ │
│ └────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────┘

┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  Pre-Feeder     │  │  Feeder         │  │  Printing  🏷️   │
│  Health: 75.2%  │  │  Health: 82.1%  │  │  Health: 35.2%  │
│  ✅ Sehat       │  │  ✅ Sehat       │  │  🔴 Kritis      │
│                 │  │                 │  │  📦 AUTO-PRED   │
└─────────────────┘  └─────────────────┘  └─────────────────┘
```

---

## 🎉 Success Indicators

You'll know it's working when you see:

1. ✅ **Badge pulsing** on critical component
2. ✅ **Orange info box** in component card
3. ✅ **Global banner** slides down from top
4. ✅ **Backend logs** show "AUTO-PREDICTION COMPLETED"
5. ✅ **Prediction duration** displayed correctly
6. ✅ **Dismiss button** works
7. ✅ **Auto-refresh** updates every 5 seconds

---

## 📞 Need Help?

### Check Documentation:

- **Backend**: `Backend/Documentation/AUTO_PREDICTION_TRIGGER.md`
- **Frontend**: `Frontend/FRONTEND_AUTO_PREDICTION_INTEGRATION.md`
- **Implementation**: `Backend/Documentation/IMPLEMENTATION_SUMMARY.md`

### Run Tests:

```bash
# Backend tests
cd Backend
python tests/test_auto_trigger.py

# Expected: TEST 4 should pass (Force Critical Condition)
```

### Common Commands:

```bash
# Check backend status
curl http://localhost:5000/api/health

# Monitor logs
tail -f Backend/logs/app.log | grep "AUTO"

# Restart services
# Backend: Ctrl+C then python app.py
# Frontend: Ctrl+C then npm run dev
```

---

**Ready to Test?** Follow steps 1-10 above! 🚀

**Version**: 1.0  
**Last Updated**: October 23, 2025

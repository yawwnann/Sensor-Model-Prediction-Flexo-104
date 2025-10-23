# Auto-Prediction Trigger - Frontend Integration Guide

## 📋 Overview

Dokumentasi ini menjelaskan implementasi fitur **Auto-Prediction Trigger** di frontend React untuk menampilkan hasil prediksi maintenance yang dipicu secara otomatis oleh backend.

---

## 🎯 Fitur yang Diimplementasikan

### 1. **Auto-Prediction Badge di Component Card** 🏷️

- Badge "AUTO-PREDICTED" muncul di pojok kanan atas card
- Animasi pulse untuk menarik perhatian
- Menampilkan durasi prediksi maintenance

### 2. **Global Alert Banner** 🚨

- Banner besar di atas dashboard
- Menampilkan semua komponen yang ter-trigger
- Detail prediksi untuk setiap komponen
- Dapat di-dismiss oleh user
- Auto-refresh saat ada trigger baru

### 3. **Visual Indicators** 👁️

- Warna orange untuk alert
- Icon lightning (⚡) untuk auto-prediction
- Clock icon (🕐) untuk durasi
- Trending down icon (📉) untuk health kritis

---

## 📁 File Structure

```
Frontend/
├── src/
│   ├── components/
│   │   ├── ComponentCard.jsx       # ✅ Modified - Badge & detail box
│   │   ├── AutoPredictionAlert.jsx # ✅ New - Global alert banner
│   │   ├── OEEChart.jsx
│   │   ├── PredictionPanel.jsx
│   │   ├── TrendChart.jsx
│   │   └── FMEATable.jsx
│   ├── services/
│   │   └── api.js                  # No changes needed
│   ├── App.jsx                     # ✅ Modified - Import & use alert
│   ├── App.css                     # ✅ Modified - Animation
│   └── main.jsx
└── package.json
```

---

## 🔧 Implementasi Detail

### 1. ComponentCard.jsx - Badge & Info Box

#### Import Icons

```jsx
import {
  Activity,
  AlertCircle,
  CheckCircle,
  Loader2,
  Zap, // ✅ New - Lightning icon
  Clock, // ✅ New - Clock icon
} from "lucide-react";
```

#### Extract Auto-Prediction Data

```jsx
const {
  health_index = 0,
  status = "Unknown",
  color = "#6B7280",
  description = "No data",
  metrics = {},
  auto_prediction = null, // ✅ New field
} = healthData || {};

const isAutoPredicted = auto_prediction?.triggered === true;
```

#### Badge Display (Top-Right Corner)

```jsx
{
  isAutoPredicted && (
    <div className="absolute -top-2 -right-2 z-10">
      <div className="bg-orange-500 text-white px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1 shadow-lg animate-pulse">
        <Zap className="w-3 h-3" />
        AUTO-PREDICTED
      </div>
    </div>
  );
}
```

#### Detailed Info Box (Below Status)

```jsx
{
  isAutoPredicted && auto_prediction.prediction_result && (
    <div className="mb-4 p-3 bg-orange-50 border-2 border-orange-300 rounded-md">
      <div className="flex items-center gap-2 mb-2">
        <Zap className="w-4 h-4 text-orange-600" />
        <p className="text-xs font-bold text-orange-800">
          🤖 AUTO-PREDICTION TRIGGERED
        </p>
      </div>
      {auto_prediction.prediction_result.success ? (
        <>
          <div className="flex items-center gap-2 mb-1">
            <Clock className="w-4 h-4 text-orange-600" />
            <p className="text-sm font-bold text-orange-900">
              {auto_prediction.prediction_result.prediction_formatted}
            </p>
          </div>
          <p className="text-xs text-orange-700">
            Maintenance prediction duration
          </p>
          <div className="mt-2 pt-2 border-t border-orange-200">
            <p className="text-xs text-orange-600">
              ⚠️ Critical health detected (&lt;
              {auto_prediction.trigger_threshold})
            </p>
          </div>
        </>
      ) : (
        <p className="text-xs text-orange-700">
          Prediction triggered but failed:{" "}
          {auto_prediction.prediction_result.message}
        </p>
      )}
    </div>
  );
}
```

---

### 2. AutoPredictionAlert.jsx - Global Banner

#### Component Structure

```jsx
const AutoPredictionAlert = ({ healthData }) => {
  const [autoPredictedComponents, setAutoPredictedComponents] = useState([]);
  const [isDismissed, setIsDismissed] = useState(false);
  const [lastAlertTime, setLastAlertTime] = useState(null);

  useEffect(() => {
    // Find all components with auto-prediction triggered
    const components = Object.entries(healthData)
      .filter(([, data]) => data?.auto_prediction?.triggered === true)
      .map(([name, data]) => ({
        name,
        healthIndex: data.health_index,
        threshold: data.auto_prediction.trigger_threshold,
        predictionResult: data.auto_prediction.prediction_result,
      }));

    setAutoPredictedComponents(components);

    // Reset dismissed state if new predictions appear
    if (components.length > 0) {
      setIsDismissed(false);
      setLastAlertTime(new Date());
    }
  }, [healthData]);

  if (isDismissed || autoPredictedComponents.length === 0) {
    return null;
  }

  return (
    <div className="container mx-auto px-4 py-4">{/* Alert content */}</div>
  );
};
```

#### Alert Features

- **Auto-detect**: Otomatis mendeteksi komponen dengan auto-prediction
- **Multi-component**: Dapat menampilkan multiple alerts
- **Dismissible**: User dapat dismiss alert
- **Auto-reset**: Dismiss state reset saat ada trigger baru
- **Timestamp**: Menampilkan waktu trigger

---

### 3. App.jsx - Integration

#### Import Component

```jsx
import AutoPredictionAlert from "./components/AutoPredictionAlert";
```

#### Place Alert (Above Error Banner)

```jsx
{/* Auto-Prediction Alert - Global Notification */}
<AutoPredictionAlert healthData={healthData} />

{/* Error Banner */}
{error && (
  // ... error banner code
)}
```

**Why Above Error Banner?**

- Higher priority
- User sees critical predictions first
- Consistent placement

---

### 4. App.css - Animation

```css
/* Slide down animation for auto-prediction alert */
@keyframes slideDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-slide-down {
  animation: slideDown 0.5s ease-out;
}
```

**Animation Effect:**

- Smooth slide from top
- Fade in effect
- Duration: 0.5 seconds
- Easing: ease-out

---

## 🎨 Visual Design

### Color Scheme

- **Primary**: Orange (#F97316) - Alert/Warning color
- **Secondary**: Red (#EF4444) - Critical emphasis
- **Background**: Orange-50 to Red-50 gradient
- **Text**: Orange-900 for headers, Orange-700 for body

### Layout

```
┌─────────────────────────────────────────────────┐
│ 🚨 Automatic Prediction Triggered         ❌   │
│ Critical health condition detected on 2 compo... │
├─────────────────────────────────────────────────┤
│                                                 │
│ ┌─ Printing Unit ──────────────────────────┐  │
│ │ 🔻 Health: 35.2%                          │  │
│ │                                           │  │
│ │ 🕐 Predicted Maintenance Duration         │  │
│ │    2 jam 7 menit                          │  │
│ │                                           │  │
│ │ ⚠️ RECOMMENDATION: Schedule Immediate ... │  │
│ └───────────────────────────────────────────┘  │
│                                                 │
│ Alert triggered at: 10:30:45 AM                │
└─────────────────────────────────────────────────┘
```

---

## 📊 Data Flow

```
Backend API Response
       ↓
fetchComponentHealth()
       ↓
App.jsx (healthData state)
       ↓
    ┌──────┴──────┐
    ↓             ↓
ComponentCard  AutoPredictionAlert
    ↓             ↓
 Badge Box    Global Banner
```

### Response Structure

```json
{
  "component_name": "Printing Unit",
  "health_index": 35.2,
  "status": "Critical",
  "metrics": { ... },
  "auto_prediction": {           // ✅ New field
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
      "message": "Prediksi berhasil"
    }
  }
}
```

---

## 🧪 Testing

### 1. Visual Testing

**Test Scenario 1: No Auto-Prediction**

```
✅ No badge on component card
✅ No global alert banner
✅ Normal dashboard display
```

**Test Scenario 2: Single Auto-Prediction**

```
✅ Badge appears on affected component
✅ Orange info box in component card
✅ Global banner shows one alert
✅ Dismiss button works
```

**Test Scenario 3: Multiple Auto-Predictions**

```
✅ Multiple badges on affected components
✅ Global banner shows all alerts
✅ Each alert has own card
✅ All data displays correctly
```

### 2. Functional Testing

```bash
# Terminal 1: Start Backend
cd Backend
python app.py

# Terminal 2: Start Frontend
cd Frontend
npm run dev

# Terminal 3: Monitor Backend Logs
tail -f Backend/logs/app.log | grep "AUTO"
```

### 3. Trigger Testing

**Method 1: Adjust Threshold (Temporary)**

```python
# In health_service.py
CRITICAL_THRESHOLD = 80.0  # Easier to trigger
```

**Method 2: Monitor Real Data**

- Wait for actual health index to drop
- Or manipulate sensor data

**Method 3: Use Test API**

```bash
# Call health endpoint repeatedly
watch -n 2 curl http://localhost:5000/api/health/Printing
```

---

## 🎯 User Experience Flow

### Scenario: Critical Health Detected

1. **Backend Detection** (Automatic)

   - Health index drops below 40
   - Auto-prediction triggered
   - Result logged

2. **Frontend Auto-Update** (Every 5s)

   - Dashboard fetches new data
   - Detects `auto_prediction` field

3. **Visual Feedback** (Instant)

   - 🏷️ Badge appears on component card
   - 📦 Info box shows in card
   - 🚨 Global banner slides down from top
   - 🔔 Visual pulse animation

4. **User Action** (Manual)

   - User reads alert
   - User notes maintenance duration
   - User schedules maintenance
   - User dismisses alert (optional)

5. **Next Refresh** (5s later)
   - If still critical: Alert remains
   - If health improved: Alert disappears
   - If dismissed: User decision respected (until new trigger)

---

## 🔍 Debugging

### Check if Data Arrives

**In Browser Console:**

```javascript
// After page load, check healthData
// Open React DevTools → Components → App → healthData

// Or add temporary console.log in App.jsx:
console.log("Health Data:", healthData);

// Check for auto_prediction field:
Object.entries(healthData).forEach(([name, data]) => {
  if (data.auto_prediction) {
    console.log(`${name} has auto-prediction:`, data.auto_prediction);
  }
});
```

### Common Issues

**Issue 1: Badge not showing**

```
Cause: auto_prediction field not in response
Fix: Check backend logs, ensure health < 40
```

**Issue 2: Alert banner not appearing**

```
Cause: Filter logic issue or data structure
Fix: Check AutoPredictionAlert useEffect
```

**Issue 3: Animation not working**

```
Cause: CSS not loaded
Fix: Check App.css import, rebuild if needed
```

---

## 📱 Responsive Design

### Desktop (>= 1024px)

- Global banner: Full width with padding
- Component cards: 5 columns grid
- Alert cards: 2-column grid (info)

### Tablet (768px - 1023px)

- Global banner: Full width
- Component cards: 3 columns grid
- Alert cards: 1-column grid

### Mobile (< 768px)

- Global banner: Full width, stacked
- Component cards: 1-2 columns
- Alert cards: 1-column, compact

---

## 🚀 Deployment Checklist

- [ ] Test with real backend data
- [ ] Verify all animations work
- [ ] Check responsive design
- [ ] Test dismiss functionality
- [ ] Verify auto-refresh works
- [ ] Test with multiple triggers
- [ ] Check browser compatibility
- [ ] Optimize performance
- [ ] Add error boundaries (optional)
- [ ] Document for team

---

## 📚 Related Documentation

- **Backend**: `Backend/Documentation/AUTO_PREDICTION_TRIGGER.md`
- **API**: `Backend/Documentation/README.md`
- **Components**: `Frontend/COMPONENTS_GUIDE.md`
- **Frontend**: `Frontend/FRONTEND_DOCS.md`

---

## 💡 Future Enhancements

### Potential Features

1. **Sound Notification**: Play alert sound on trigger
2. **Browser Notification**: Desktop notification API
3. **Email Alert**: Send email to maintenance team
4. **History Log**: Store alert history in localStorage
5. **Analytics**: Track trigger frequency
6. **Custom Actions**: Quick action buttons (Schedule, Acknowledge, Dismiss)
7. **Multi-language**: i18n support
8. **Dark Mode**: Theme support

### Implementation Ideas

```jsx
// Sound notification
const playAlertSound = () => {
  const audio = new Audio("/alert-sound.mp3");
  audio.play();
};

// Browser notification
if (Notification.permission === "granted") {
  new Notification("Auto-Prediction Triggered", {
    body: `Critical health on ${component.name}`,
    icon: "/icon.png",
  });
}

// History tracking
const saveToHistory = (component, prediction) => {
  const history = JSON.parse(localStorage.getItem("alert_history") || "[]");
  history.push({
    component,
    prediction,
    timestamp: new Date().toISOString(),
  });
  localStorage.setItem("alert_history", JSON.stringify(history));
};
```

---

## ✅ Summary

**What We Built:**

1. ✅ Auto-prediction badge on component cards
2. ✅ Detailed info box in cards
3. ✅ Global alert banner for all triggers
4. ✅ Smooth animations and transitions
5. ✅ Dismissible alerts
6. ✅ Responsive design
7. ✅ Clear visual indicators

**Key Benefits:**

- 🎯 **Proactive**: User immediately sees critical predictions
- 👁️ **Visual**: Clear, eye-catching design
- 📊 **Informative**: All relevant data displayed
- 🔄 **Automatic**: No manual refresh needed
- 🎨 **Professional**: Polished UI/UX

---

**Version**: 1.0  
**Last Updated**: October 23, 2025  
**Author**: Frontend Development Team  
**Status**: ✅ COMPLETE

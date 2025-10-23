# 🎨 FlexoTwin Frontend Components Documentation

## 📋 Component Overview

Frontend terdiri dari 6 komponen utama yang terintegrasi:

### 1. **App.jsx** - Main Application

- Orchestrator untuk semua komponen
- Handle data fetching dan state management
- Auto-refresh setiap 5 detik
- Layout responsive

### 2. **ComponentCard.jsx** - Health Status Card

- Menampilkan health index per komponen
- OEE metrics (Availability, Performance, Quality)
- Color-coded status indicators
- Loading dan error states

### 3. **OEEChart.jsx** - OEE Analysis & Charts

- Bar chart untuk OEE components
- Line chart untuk OEE trend
- Overall OEE metrics cards
- Analysis & recommendations

### 4. **TrendChart.jsx** - Health Index Trend

- Multi-line chart untuk 5 komponen
- Historical data (last 50 points)
- Statistics (latest, average, trend)
- Color-coded per component

### 5. **FMEATable.jsx** - FMEA Analysis

- FMEA table dengan RPN calculation
- Expandable rows untuk recommendations
- Component selector dropdown
- Risk priority indicators

### 6. **PredictionPanel.jsx** - ML Prediction

- Input form untuk prediction
- Color-coded results
- Recommendations based on prediction
- Error handling

---

## 📊 Dashboard Sections

### Section 1: Overall Statistics

4 info cards menampilkan:

- 🎯 Total Components
- ✅ Healthy Components (Health >= 80%)
- ⚠️ Need Attention (Health < 80%)
- 📊 Overall Health (Average)

### Section 2: Component Health Status

Grid 5 cards untuk menampilkan:

- Pre-Feeder status
- Feeder status
- Printing status
- Slotter status
- Stacker status

Setiap card menampilkan:

- Health Index dengan progress bar
- Status (Healthy/Warning/Danger)
- OEE, Availability, Performance, Quality

### Section 3: OEE Analysis

Comprehensive OEE analysis dengan:

- 4 metric cards (OEE, Availability, Performance, Quality)
- OEE Formula display
- Bar chart: OEE components by machine
- Line chart: OEE trend over time
- Analysis & recommendations

### Section 4: Trend & Prediction

2-column layout:

- **Left (2 cols):** Health Index Trend Chart
  - Multi-line chart untuk 5 komponen
  - Statistics per component
  - Last 50 data points
- **Right (1 col):** ML Prediction Panel
  - Input: Total Produksi & Produk Cacat
  - Output: Maintenance Duration (menit)
  - Recommendations

### Section 5: FMEA Analysis

FMEA table dengan features:

- Component selector dropdown
- RPN score badge
- Expandable rows untuk recommendations
- Risk priority color coding
- Legend untuk S, O, D, RPN

---

## 🎨 Color Scheme

### Health Index Colors

- 🟢 **Healthy (>= 80%)**: Green (#10B981)
- 🟡 **Warning (60-79%)**: Yellow (#F59E0B)
- 🔴 **Danger (< 60%)**: Red (#EF4444)

### OEE Component Colors

- 🔵 **OEE**: Blue (#3B82F6)
- 🟢 **Availability**: Green (#10B981)
- 🟡 **Performance**: Yellow (#F59E0B)
- 🟣 **Quality**: Purple (#8B5CF6)

### Component Trend Colors

- 🔴 **Pre-Feeder**: Red (#EF4444)
- 🟠 **Feeder**: Orange (#F59E0B)
- 🟢 **Printing**: Green (#10B981)
- 🔵 **Slotter**: Blue (#3B82F6)
- 🟣 **Stacker**: Purple (#8B5CF6)

---

## 📈 Data Flow

```
Backend API (Flask)
    ↓
fetchAllComponentsHealth()
    ↓
App.jsx State Management
    ├→ healthData (current)
    ├→ healthHistory (last 50 points)
    ├→ oeeHistory (last 50 points)
    └→ timestamps (last 50 points)
    ↓
Components Rendering
    ├→ ComponentCard (5x)
    ├→ OEEChart
    ├→ TrendChart
    ├→ FMEATable
    └→ PredictionPanel
```

---

## 🔄 Auto-Refresh Strategy

```javascript
useEffect(() => {
  fetchData(); // Initial fetch

  const interval = setInterval(() => {
    fetchData(); // Auto refresh every 5s
  }, REFRESH_INTERVAL);

  return () => clearInterval(interval); // Cleanup
}, []);
```

### What happens on each refresh:

1. Fetch new data from API
2. Update healthData state
3. Append to healthHistory (keep last 50)
4. Calculate OEE averages
5. Append to oeeHistory (keep last 50)
6. Add timestamp
7. Re-render all components

---

## 📊 Charts Configuration

### Recharts Library

All charts use `recharts` library:

- **BarChart**: OEE components comparison
- **LineChart**: Trend visualization
- **ResponsiveContainer**: Auto-resize
- **Tooltip**: Interactive hover info
- **Legend**: Component labels

### Chart Features

- ✅ Responsive width/height
- ✅ Custom tooltips
- ✅ Grid lines
- ✅ Axis labels
- ✅ Color-coded data
- ✅ Interactive legends
- ✅ Hover effects

---

## 🎯 Key Features

### Real-time Monitoring

- ✅ Auto-refresh every 5 seconds
- ✅ Manual refresh button
- ✅ Last update timestamp
- ✅ Loading indicators
- ✅ Error handling

### Data Visualization

- ✅ Health index progress bars
- ✅ OEE component breakdown
- ✅ Multi-line trend charts
- ✅ Bar chart comparisons
- ✅ Color-coded indicators

### Interactive Elements

- ✅ Expandable FMEA rows
- ✅ Component selector dropdown
- ✅ Hover tooltips on charts
- ✅ Clickable refresh button
- ✅ ML prediction form

### Responsive Design

- ✅ Mobile-friendly layout
- ✅ Grid-based responsive cards
- ✅ Adaptive chart sizing
- ✅ Flexible column layout
- ✅ Tailwind CSS utilities

---

## 🚀 Performance Optimizations

### State Management

- Keep only last 50 data points
- Prevent unnecessary re-renders
- Efficient data structure

### API Calls

- Promise.allSettled for parallel fetches
- Error handling per component
- Timeout configuration

### Rendering

- Conditional rendering for loading states
- Lazy loading for charts
- Optimized re-renders

---

## 🐛 Error Handling

### Connection Errors

- Display error banner
- Helpful error messages
- Continue showing last known data

### Component Errors

- Individual error cards
- Specific error messages
- Graceful degradation

### Prediction Errors

- Error alert in prediction panel
- API error details
- Input validation

---

## 📱 Responsive Breakpoints

```css
Mobile: < 768px     → 1 column layout
Tablet: 768-1024px  → 2 column layout
Desktop: > 1024px   → 3+ column layout
```

### Grid Configurations

- **Stats Cards**: 1-4 columns (responsive)
- **Health Cards**: 1-5 columns (responsive)
- **Trend/Prediction**: 1-3 columns (responsive)
- **FMEA Table**: Full width (scrollable)

---

## 🎓 Component Props

### ComponentCard

```jsx
<ComponentCard
  name="Pre-Feeder"
  healthData={{
    health_index: 85.5,
    status: "Sehat",
    color: "#10B981",
    oee: 90.2,
    availability_rate: 92.0,
    performance_rate: 95.0,
    quality_rate: 98.5,
  }}
  isLoading={false}
/>
```

### OEEChart

```jsx
<OEEChart
  componentsData={healthData}
  oeeHistory={[
    { oee: 90, availability: 92, performance: 95, quality: 98 },
    ...
  ]}
/>
```

### TrendChart

```jsx
<TrendChart
  healthHistory={{
    'Pre-Feeder': [85, 86, 87, ...],
    'Feeder': [80, 81, 82, ...],
    ...
  }}
  timestamps={['10:30:00', '10:30:05', ...]}
/>
```

### FMEATable

```jsx
<FMEATable
  components={["Pre-Feeder", "Feeder", "Printing", "Slotter", "Stacker"]}
/>
```

---

## 🔍 FMEA Data Structure

```javascript
{
  'Pre-Feeder': {
    rpn: 280,
    failures: [
      {
        mode: 'Paper Jam',
        cause: 'Roller kotor/aus',
        effect: 'Produksi terhenti',
        severity: 8,    // 1-10
        occurrence: 7,  // 1-10
        detection: 5,   // 1-10
        // RPN = S × O × D = 8 × 7 × 5 = 280
      },
      ...
    ]
  },
  ...
}
```

### RPN Risk Levels

- 🔴 **High Risk (> 250)**: Immediate action required
- 🟡 **Medium Risk (150-250)**: Schedule maintenance
- 🟢 **Low Risk (< 150)**: Routine monitoring

---

## 📚 Libraries Used

```json
{
  "react": "^18.3.1",
  "axios": "^1.7.9",
  "recharts": "^2.15.0",
  "lucide-react": "^0.468.0",
  "tailwindcss": "^4.1.0"
}
```

---

## 🎉 Summary

Dashboard ini menyediakan:

- ✅ **5 Component Health Cards** dengan detail OEE metrics
- ✅ **OEE Analysis Section** dengan 2 charts
- ✅ **Health Trend Chart** untuk historical data
- ✅ **ML Prediction Panel** untuk maintenance forecast
- ✅ **FMEA Analysis Table** dengan RPN calculation
- ✅ **Auto-refresh** setiap 5 detik
- ✅ **Responsive design** untuk mobile/tablet/desktop
- ✅ **Complete error handling** untuk reliability

**Total Visualizations:** 4 charts + 5 cards + 1 table + 4 info cards = **14 data points**

---

**Last Updated:** October 22, 2025  
**Version:** 2.0.0  
**Framework:** React 18 + Vite + Tailwind CSS + Recharts

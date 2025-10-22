import time
from typing import List, Tuple, Dict, Any
from datetime import datetime, timedelta
from collections import deque

import pandas as pd
import requests
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# 1) Page configuration
st.set_page_config(
    page_title="FlexoTwin Dashboard",
    page_icon="⚙",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS untuk styling
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .status-healthy {
        background-color: #d4edda;
        color: #155724;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    .status-warning {
        background-color: #fff3cd;
        color: #856404;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    .status-danger {
        background-color: #f8d7da;
        color: #721c24;
        padding: 10px;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    .icon-box {
        display: inline-block;
        padding: 5px 10px;
        background-color: #e9ecef;
        border-radius: 5px;
        margin-right: 10px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚙ FlexoTwin Digital Twin Dashboard")
st.markdown("### Smart Maintenance 4.0 - Real-Time Monitoring System")

# 2) Config
API_BASE_URL = "http://localhost:5000/api/health"
COMPONENTS: List[str] = [
    "Pre-Feeder",
    "Feeder",
    "Printing",
    "Slotter",
    "Stacker",
]
REFRESH_SECONDS = 5
REQUEST_TIMEOUT = 12
MAX_RETRIES = 2

# 3) Session State untuk menyimpan historical data
if 'health_history' not in st.session_state:
    st.session_state.health_history = {comp: deque(maxlen=50) for comp in COMPONENTS}
    st.session_state.oee_history = deque(maxlen=50)
    st.session_state.overall_health_history = deque(maxlen=50)
    st.session_state.timestamps = deque(maxlen=50)
    st.session_state.machine_logs = deque(maxlen=20)
    st.session_state.refresh_counter = 0
    st.session_state.stop_pressed = False
    st.session_state.last_update = None
    # Cache untuk optimasi refresh
    st.session_state.cached_components_data = {}
    st.session_state.last_fetch_time = 0
    st.session_state.cached_current_time = datetime.now()

# FMEA Data (Static - dari analisis Anda)
FMEA_DATA = {
    "Pre-Feeder": {
        "RPN": 280,
        "failures": [
            {"mode": "Paper Jam", "cause": "Roller kotor/aus", "effect": "Produksi terhenti", "severity": 8, "occurrence": 7, "detection": 5},
            {"mode": "Feeding Error", "cause": "Sensor misalignment", "effect": "Kualitas print buruk", "severity": 7, "occurrence": 6, "detection": 6},
        ]
    },
    "Feeder": {
        "RPN": 252,
        "failures": [
            {"mode": "Double Feed", "cause": "Tekanan suction lemah", "effect": "Material waste", "severity": 7, "occurrence": 6, "detection": 6},
            {"mode": "Skewed Feed", "cause": "Guide tidak sejajar", "effect": "Registrasi tidak akurat", "severity": 8, "occurrence": 5, "detection": 7},
        ]
    },
    "Printing": {
        "RPN": 320,
        "failures": [
            {"mode": "Ink Smudging", "cause": "Anilox roller aus", "effect": "Kualitas print rendah", "severity": 9, "occurrence": 6, "detection": 6},
            {"mode": "Registration Error", "cause": "Sensor tidak kalibrasi", "effect": "Print tidak tepat", "severity": 8, "occurrence": 7, "detection": 6},
        ]
    },
    "Slotter": {
        "RPN": 210,
        "failures": [
            {"mode": "Blade Tumpul", "cause": "Wear and tear normal", "effect": "Slot tidak rapi", "severity": 7, "occurrence": 6, "detection": 5},
            {"mode": "Misalignment", "cause": "Getaran berlebih", "effect": "Dimensi tidak akurat", "severity": 8, "occurrence": 5, "detection": 6},
        ]
    },
    "Stacker": {
        "RPN": 180,
        "failures": [
            {"mode": "Stack Collapse", "cause": "Kecepatan terlalu tinggi", "effect": "Produk rusak", "severity": 6, "occurrence": 5, "detection": 6},
            {"mode": "Counting Error", "cause": "Sensor kotor", "effect": "Salah hitung output", "severity": 5, "occurrence": 6, "detection": 6},
        ]
    }
}

# 3) Helper Functions

def fetch_health(component: str) -> Tuple[bool, dict | str]:
    """Fetch health info for a component from the Flask API with retry logic.

    Returns:
        (ok, data_or_error)
        - ok True => data_or_error is dict with keys like {"component_name", "health_index", "status"}
        - ok False => data_or_error is an error string
    """
    url = f"{API_BASE_URL}/{component}"
    last_error = None
    
    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()
            return True, data
        except requests.exceptions.Timeout:
            last_error = f"Timeout (attempt {attempt + 1}/{MAX_RETRIES})"
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
                continue
        except requests.exceptions.ConnectionError as e:
            last_error = f"Connection error: {str(e)[:50]}"
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
                continue
        except requests.exceptions.HTTPError as e:
            return False, f"HTTP {e.response.status_code}: {e.response.text[:100]}"
        except requests.exceptions.RequestException as e:
            last_error = f"Request error: {str(e)[:50]}"
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
                continue
        except ValueError:
            return False, "Invalid JSON response"
    
    return False, last_error or "Unknown error"


def get_status_color(health_index: float) -> str:
    """Return status color based on health index"""
    if health_index >= 70:
        return "healthy"
    elif health_index >= 50:
        return "warning"
    else:
        return "danger"


def get_status_text(health_index: float) -> str:
    """Return status text based on health index"""
    if health_index >= 70:
        return "▲ Sehat"
    elif health_index >= 50:
        return "■ Perlu Perhatian"
    else:
        return "● Kritis"


def calculate_overall_metrics(components_data: Dict[str, Any]) -> Dict[str, Any]:
    """Calculate overall machine metrics from components data"""
    health_indices = []
    oee_values = []
    
    for comp_name, data in components_data.items():
        if isinstance(data, dict):
            if 'health_index' in data and isinstance(data['health_index'], (int, float)):
                health_indices.append(data['health_index'])
            # OEE Score ada di metrics
            metrics = data.get('metrics', {})
            if 'oee_score' in metrics and isinstance(metrics['oee_score'], (int, float)):
                oee_values.append(metrics['oee_score'])
    
    overall_health = sum(health_indices) / len(health_indices) if health_indices else 0
    overall_oee = sum(oee_values) / len(oee_values) if oee_values else 0
    
    # Determine operational status
    if overall_health >= 70:
        status = "Beroperasi Normal"
    elif overall_health >= 50:
        status = "Perlu Perhatian"
    else:
        status = "Downtime/Kritis"
    
    return {
        "overall_health": overall_health,
        "overall_oee": overall_oee,
        "status": status,
        "component_count": len(health_indices)
    }


def create_trend_chart(history_data: Dict) -> go.Figure:
    """Create trend chart for health index and OEE"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Overall Health Index Trend', 'OEE Trend'),
        vertical_spacing=0.15
    )
    
    timestamps = list(st.session_state.timestamps)
    
    # Health Index Trend
    if st.session_state.overall_health_history:
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=list(st.session_state.overall_health_history),
                mode='lines+markers',
                name='Health Index',
                line=dict(color='#2E86AB', width=3),
                fill='tozeroy',
                fillcolor='rgba(46, 134, 171, 0.2)'
            ),
            row=1, col=1
        )
    
    # OEE Trend
    if st.session_state.oee_history:
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=list(st.session_state.oee_history),
                mode='lines+markers',
                name='OEE',
                line=dict(color='#06A77D', width=3),
                fill='tozeroy',
                fillcolor='rgba(6, 167, 125, 0.2)'
            ),
            row=2, col=1
        )
    
    fig.update_xaxes(title_text="Time", row=2, col=1)
    fig.update_yaxes(title_text="Health Index (%)", row=1, col=1)
    fig.update_yaxes(title_text="OEE (%)", row=2, col=1)
    
    fig.update_layout(
        height=600,
        showlegend=True,
        hovermode='x unified',
        template='plotly_white'
    )
    
    return fig


# 4) Dashboard setup - Sidebar controls
with st.sidebar:
    st.header("▼ Dashboard Controls")
    
    # Stop button
    if st.button("■ Stop Auto-Refresh", type="secondary", use_container_width=True):
        st.session_state.stop_pressed = True
    
    if st.button("▶ Resume Auto-Refresh", type="primary", use_container_width=True):
        st.session_state.stop_pressed = False
    
    st.divider()
    
    # Refresh interval
    st.markdown(f"**Refresh Interval:** {REFRESH_SECONDS} seconds")
    st.markdown(f"**API Endpoint:** `{API_BASE_URL}`")
    st.markdown(f"**Max History:** 50 data points")
    
    st.divider()
    
    # ====================================================================
    # MODUL PREDIKSI MAINTENANCE
    # ====================================================================
    st.header("🔧 Modul Prediksi Maintenance")
    st.markdown("Prediksi durasi maintenance berdasarkan data produksi")
    
    # Input form untuk prediksi
    total_produksi = st.number_input(
        "📦 Total Produksi (Pcs)", 
        min_value=0, 
        value=10000,
        step=100,
        help="Masukkan total unit yang diproduksi"
    )
    
    produk_cacat = st.number_input(
        "❌ Produk Cacat (Pcs)", 
        min_value=0, 
        value=500,
        step=10,
        help="Masukkan jumlah produk yang cacat/reject"
    )
    
    # Tombol untuk menjalankan prediksi
    if st.button("🚀 Jalankan Prediksi", type="primary", use_container_width=True):
        # Buat payload untuk API
        payload = {
            "total_produksi": total_produksi,
            "produk_cacat": produk_cacat
        }
        
        # API endpoint untuk prediksi
        predict_url = "http://localhost:5000/api/predict/maintenance"
        
        try:
            # Kirim request ke backend
            with st.spinner("🔄 Memproses prediksi..."):
                response = requests.post(
                    predict_url, 
                    json=payload,
                    timeout=10
                )
            
            # Cek status response
            if response.status_code == 200:
                result = response.json()
                
                # Backend mengembalikan 'prediction' bukan 'prediksi_durasi_menit'
                prediksi_durasi = result.get('prediction', 0)
                prediction_formatted = result.get('prediction_formatted', '')
                
                # Tampilkan hasil prediksi
                st.success("✅ Prediksi Berhasil!")
                
                # Metric dengan format yang jelas
                hours = int(prediksi_durasi // 60)
                minutes = int(prediksi_durasi % 60)
                
                st.metric(
                    label="⏱️ Durasi Maintenance Prediksi",
                    value=f"{prediksi_durasi:.2f} menit",
                    delta=f"{hours} jam {minutes} menit" if hours > 0 else f"{minutes} menit"
                )
                
                # Informasi tambahan
                defect_rate = (produk_cacat / total_produksi * 100) if total_produksi > 0 else 0
                st.info(f"📊 **Defect Rate:** {defect_rate:.2f}%")
                
                # Tampilkan metadata jika ada
                if 'metadata' in result:
                    metadata = result['metadata']
                    st.caption(f"🤖 Model: {metadata.get('model_type', 'N/A')} | Method: {metadata.get('calculation_method', 'N/A')}")
                
                # Rekomendasi berdasarkan durasi
                if prediksi_durasi > 120:
                    st.warning("⚠️ **Maintenance Lama:** Siapkan backup mesin atau jadwal ulang produksi")
                elif prediksi_durasi > 60:
                    st.info("ℹ️ **Maintenance Sedang:** Pastikan spare part tersedia")
                else:
                    st.success("✅ **Maintenance Cepat:** Dapat dilakukan saat shift break")
                
            else:
                # Tampilkan error jika status bukan 200
                st.error(f"❌ Error {response.status_code}: {response.text[:100]}")
                
        except requests.exceptions.ConnectionError:
            st.error("❌ **Connection Error:** Backend tidak dapat dihubungi. Pastikan Flask app berjalan di port 5000.")
        except requests.exceptions.Timeout:
            st.error("❌ **Timeout:** Request memakan waktu terlalu lama. Coba lagi.")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ **Request Error:** {str(e)[:100]}")
        except Exception as e:
            st.error(f"❌ **Unexpected Error:** {str(e)[:100]}")
    
    st.divider()
    
    # Component selection for FMEA
    st.header("▼ FMEA Analysis")
    selected_component = st.selectbox(
        "Select Component",
        options=COMPONENTS,
        help="Select a component to view its FMEA analysis"
    )

# Check if auto-refresh is stopped
if st.session_state.stop_pressed:
    st.info("▲ Auto-refresh dihentikan. Klik 'Resume Auto-Refresh' di sidebar untuk melanjutkan.")
    st.stop()

# ====================================================================
# SMART REFRESH MECHANISM - Cache with Timestamp Check
# ====================================================================
current_timestamp = time.time()
time_since_last_fetch = current_timestamp - st.session_state.last_fetch_time
should_fetch_new_data = time_since_last_fetch >= REFRESH_SECONDS

if should_fetch_new_data:
    # === FETCH NEW DATA (Silent, no loading indicator) ===
    current_time = datetime.now()
    
    components_data = {}
    for component in COMPONENTS:
        ok, result = fetch_health(component)
        if ok and isinstance(result, dict):
            components_data[component] = result
        else:
            components_data[component] = {"error": result}
    
    # Calculate overall metrics
    overall_metrics = calculate_overall_metrics(components_data)
    
    # Store historical data
    st.session_state.timestamps.append(current_time)
    st.session_state.overall_health_history.append(overall_metrics['overall_health'])
    st.session_state.oee_history.append(overall_metrics['overall_oee'])
    st.session_state.last_update = current_time
    
    # Add log entry
    log_entry = {
        "timestamp": current_time.strftime("%Y-%m-%d %H:%M:%S"),
        "health": f"{overall_metrics['overall_health']:.1f}%",
        "oee": f"{overall_metrics['overall_oee']:.1f}%",
        "status": overall_metrics['status']
    }
    st.session_state.machine_logs.append(log_entry)
    
    # Update cache
    st.session_state.cached_components_data = components_data
    st.session_state.cached_overall_metrics = overall_metrics
    st.session_state.cached_current_time = current_time
    st.session_state.last_fetch_time = current_timestamp
    st.session_state.refresh_counter += 1
else:
    # === USE CACHED DATA (Silent) ===
    components_data = st.session_state.cached_components_data
    overall_metrics = st.session_state.get('cached_overall_metrics', {})
    current_time = st.session_state.cached_current_time

# ====================================================================
# SECTION 1: RINGKASAN KONDISI MESIN (TAMPILAN UTAMA)
# ====================================================================
st.markdown("## ▣ Ringkasan Kondisi Mesin")

# Placeholder untuk metrics yang akan di-update
metrics_placeholder = st.empty()

with metrics_placeholder.container():
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        health_value = overall_metrics['overall_health']
        st.metric(
            label="◆ Overall Health Index",
            value=f"{health_value:.1f}%",
            delta=get_status_text(health_value),
            help="Skor kesehatan gabungan dari semua komponen"
        )
    
    with col2:
        oee_value = overall_metrics['overall_oee']
        st.metric(
            label="◆ Overall OEE Score",
            value=f"{oee_value:.1f}%",
            delta="Real-Time",
            help="Overall Equipment Effectiveness - metrik kinerja utama"
        )
    
    with col3:
        status = overall_metrics['status']
        status_color = get_status_color(health_value)
        st.metric(
            label="◆ Status Operasional",
            value=status,
            help="Status operasional mesin saat ini"
        )
    
    with col4:
        st.metric(
            label="◆ Components Monitored",
            value=f"{overall_metrics['component_count']}/{len(COMPONENTS)}",
            help="Jumlah komponen yang sedang dimonitor"
        )

# Status indicator placeholder
status_placeholder = st.empty()
with status_placeholder.container():
    if health_value >= 70:
        st.markdown('<div class="status-healthy">▲ Mesin Beroperasi Normal</div>', unsafe_allow_html=True)
    elif health_value >= 50:
        st.markdown('<div class="status-warning">■ Mesin Perlu Perhatian</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-danger">● Mesin dalam Kondisi Kritis</div>', unsafe_allow_html=True)

st.divider()

# ====================================================================
# SECTION 1.5: OEE COMPONENTS DETAIL 
# ====================================================================
st.markdown("## ▣ Komponen OEE Detail")
st.markdown("### Overall Equipment Effectiveness (OEE) = Availability × Performance × Quality")

# Calculate overall OEE components
availability_values = []
performance_values = []
quality_values = []

for component in COMPONENTS:
    data = components_data.get(component, {})
    if 'error' not in data:
        metrics = data.get('metrics', {})
        availability_values.append(metrics.get('availability_rate', 0))
        performance_values.append(metrics.get('performance_rate', 0))
        quality_values.append(metrics.get('quality_rate', 0))

# Calculate averages
avg_availability = sum(availability_values) / len(availability_values) if availability_values else 0
avg_performance = sum(performance_values) / len(performance_values) if performance_values else 0
avg_quality = sum(quality_values) / len(quality_values) if quality_values else 0
calculated_oee = (avg_availability / 100) * (avg_performance / 100) * (avg_quality / 100) * 100

# Placeholder untuk OEE components
oee_components_placeholder = st.empty()

with oee_components_placeholder.container():
    col_avail, col_perf, col_qual, col_oee = st.columns(4)
    
    with col_avail:
        st.markdown("### ⏰ Availability")
        st.metric(
            label="Machine Uptime",
            value=f"{avg_availability:.1f}%",
            help="Persentase waktu mesin tersedia untuk produksi"
        )
        st.progress(avg_availability / 100)
    
    with col_perf:
        st.markdown("### ⚡ Performance")
        st.metric(
            label="Speed Efficiency",
            value=f"{avg_performance:.1f}%",
            help="Efisiensi kecepatan produksi vs kecepatan ideal"
        )
        st.progress(avg_performance / 100)
    
    with col_qual:
        st.markdown("### ✓ Quality")
        st.metric(
            label="First Pass Yield",
            value=f"{avg_quality:.1f}%",
            help="Persentase produk berkualitas baik dari total produksi"
        )
        st.progress(avg_quality / 100)
    
    with col_oee:
        st.markdown("### 📊 OEE Score")
        st.metric(
            label="Overall Effectiveness",
            value=f"{calculated_oee:.1f}%",
            delta=f"Target: 85%",
            help="OEE = Availability × Performance × Quality"
        )
        if calculated_oee >= 85:
            st.success(f"Excellent: {calculated_oee:.1f}%")
        elif calculated_oee >= 70:
            st.warning(f"Good: {calculated_oee:.1f}%")
        else:
            st.error(f"Needs Improvement: {calculated_oee:.1f}%")

# OEE Breakdown Chart
st.markdown("### 📈 OEE Components Breakdown")

col_chart1, col_chart2 = st.columns(2)

with col_chart1:
    # Individual component OEE chart
    fig_components = go.Figure()

    for i, component in enumerate(COMPONENTS):
        data = components_data.get(component, {})
        if 'error' not in data:
            metrics = data.get('metrics', {})
            avail = metrics.get('availability_rate', 0)
            perf = metrics.get('performance_rate', 0)
            qual = metrics.get('quality_rate', 0)
            
            fig_components.add_trace(go.Bar(
                name=component,
                x=['Availability', 'Performance', 'Quality'],
                y=[avail, perf, qual],
                text=[f'{avail:.1f}%', f'{perf:.1f}%', f'{qual:.1f}%'],
                textposition='auto',
            ))

    fig_components.update_layout(
        title='OEE Components by Machine',
        xaxis_title='OEE Components',
        yaxis_title='Percentage (%)',
        barmode='group',
        height=400,
        yaxis=dict(range=[0, 100]),
        template='plotly_white'
    )

    st.plotly_chart(fig_components, use_container_width=True, key=f"oee_comp_{st.session_state.refresh_counter}")

with col_chart2:
    # Overall OEE gauge chart
    fig_gauge = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = calculated_oee,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "Overall OEE"},
        delta = {'reference': 85, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge = {
            'axis': {'range': [None, 100]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [0, 50], 'color': "lightgray"},
                {'range': [50, 70], 'color': "yellow"},
                {'range': [70, 85], 'color': "orange"},
                {'range': [85, 100], 'color': "green"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': 85
            }
        }
    ))

    fig_gauge.update_layout(height=400)
    st.plotly_chart(fig_gauge, use_container_width=True, key=f"oee_gauge_{st.session_state.refresh_counter}")

# OEE Analysis Text
col_analysis1, col_analysis2 = st.columns(2)

with col_analysis1:
    st.markdown("#### 📋 OEE Analysis")
    if calculated_oee >= 85:
        st.success("**Excellent Performance!** ✅")
        st.write("OEE > 85% menunjukkan kinerja world-class manufacturing")
    elif calculated_oee >= 70:
        st.warning("**Good Performance** ⚠️")
        st.write("OEE 70-85% menunjukkan kinerja yang baik dengan ruang untuk improvement")
    else:
        st.error("**Needs Improvement** ❌")
        st.write("OEE < 70% memerlukan analisis mendalam dan perbaikan segera")

with col_analysis2:
    st.markdown("#### 🎯 Improvement Opportunities")
    
    if availability_values and performance_values and quality_values:
        min_avail = min(availability_values)
        min_perf = min(performance_values)
        min_qual = min(quality_values)

        if min_avail < min_perf and min_avail < min_qual:
            st.write("🔧 **Focus on Availability**: Reduce downtime dan setup time")
        elif min_perf < min_qual:
            st.write("⚡ **Focus on Performance**: Optimize speed dan eliminate bottlenecks")
        else:
            st.write("✓ **Focus on Quality**: Reduce defects dan rework")

st.divider()

# ====================================================================
# SECTION 2: STATUS KESEHATAN PER KOMPONEN
# ====================================================================
st.markdown("## ▣ Status Kesehatan per Komponen")

# Placeholder untuk component status
components_placeholder = st.empty()

with components_placeholder.container():
    cols = st.columns(len(COMPONENTS))
    
    for i, component in enumerate(COMPONENTS):
        with cols[i]:
            data = components_data.get(component, {})
            
            if 'error' not in data:
                health_idx = data.get('health_index', 0)
                metrics = data.get('metrics', {})
                oee_score = metrics.get('oee_score', 0)
                availability = metrics.get('availability_rate', 0)
                performance = metrics.get('performance_rate', 0)
                quality = metrics.get('quality_rate', 0) 
                rpn = FMEA_DATA[component]['RPN']
                
                # Store component history
                st.session_state.health_history[component].append(health_idx)
                
                # Determine color
                status_color = get_status_color(health_idx)
                
                # Component card
                if status_color == "healthy":
                    st.success(f"**{component}**")
                elif status_color == "warning":
                    st.warning(f"**{component}**")
                else:
                    st.error(f"**{component}**")
                
                # Metrics
                st.metric("Health Index", f"{health_idx:.1f}%")
                st.metric("OEE Score", f"{oee_score:.1f}%")
                
                # Details in expander
                with st.expander("▼ Detail Metrics"):
                    st.write("**OEE Components:**")
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.write(f"• Availability: {availability:.1f}%")
                        st.write(f"• Performance: {performance:.1f}%")
                    with col_b:
                        st.write(f"• Quality: {quality:.1f}%")
                        st.write(f"• RPN Score: {rpn}")
                    st.write(f"**Status:** {get_status_text(health_idx)}")
                    
                    # Mini OEE breakdown chart for this component
                    fig_mini = go.Figure(data=[
                        go.Bar(name='OEE Components', 
                               x=['Availability', 'Performance', 'Quality'],
                               y=[availability, performance, quality],
                               text=[f'{availability:.1f}%', f'{performance:.1f}%', f'{quality:.1f}%'],
                               textposition='auto')
                    ])
                    fig_mini.update_layout(
                        title=f'{component} OEE Breakdown',
                        height=250,
                        yaxis=dict(range=[0, 100]),
                        template='plotly_white'
                    )
                    st.plotly_chart(fig_mini, key=f"fig_mini_{i}_{st.session_state.refresh_counter}", use_container_width=True)
            else:
                st.error(f"**{component}**")
                st.warning("Data tidak tersedia")
                st.caption(data.get('error', 'Unknown error'))

st.divider()

# ====================================================================
# SECTION 3: GRAFIK TREN DAN LOG HISTORIS
# ====================================================================
st.markdown("## ▣ Grafik Tren dan Log Historis")

col_chart, col_logs = st.columns([2, 1])

# Placeholder untuk trend chart
with col_chart:
    st.markdown("### Tren Performa")
    trend_chart_placeholder = st.empty()
    
    with trend_chart_placeholder.container():
        if len(st.session_state.timestamps) > 1:
            trend_chart = create_trend_chart(st.session_state)
            st.plotly_chart(trend_chart, use_container_width=True, key=f"trend_{st.session_state.refresh_counter}")
        else:
            st.info("▣ Mengumpulkan data untuk grafik tren... (minimum 2 data points)")

# Placeholder untuk logs
with col_logs:
    st.markdown("### ▣ Log Status Terakhir")
    logs_placeholder = st.empty()
    
    with logs_placeholder.container():
        if st.session_state.machine_logs:
            logs_df = pd.DataFrame(list(st.session_state.machine_logs))
            st.dataframe(
                logs_df.tail(10),
                use_container_width=True,
                hide_index=True,
                height=400
            )
        else:
            st.info("Belum ada log tersedia")

st.divider()

# ====================================================================
# SECTION 4: ANALISIS AKAR MASALAH (FMEA)
# ====================================================================
st.markdown("## ▣ Analisis Akar Masalah (FMEA)")

if selected_component:
    fmea_info = FMEA_DATA[selected_component]

    col_fmea1, col_fmea2 = st.columns([1, 2])

    with col_fmea1:
        st.markdown(f"### {selected_component}")
        st.metric("Risk Priority Number (RPN)", fmea_info['RPN'])
        
        # Risk level indicator
        if fmea_info['RPN'] >= 300:
            st.error("▲ Risk Level: HIGH")
        elif fmea_info['RPN'] >= 200:
            st.warning("■ Risk Level: MEDIUM")
        else:
            st.success("● Risk Level: LOW")

    with col_fmea2:
        st.markdown("### Potential Failure Modes")
        
        # Create FMEA table
        fmea_df = pd.DataFrame(fmea_info['failures'])
        
        st.dataframe(
            fmea_df[['mode', 'cause', 'effect', 'severity', 'occurrence', 'detection']].rename(columns={
                'mode': 'Failure Mode',
                'cause': 'Potential Cause',
                'effect': 'Effect',
                'severity': 'S',
                'occurrence': 'O',
                'detection': 'D'
            }),
            use_container_width=True,
            hide_index=True
        )
        
        # Calculate RPN for each failure
        st.markdown("#### RPN Calculation")
        for failure in fmea_info['failures']:
            rpn = failure['severity'] * failure['occurrence'] * failure['detection']
            st.caption(f"**{failure['mode']}:** S×O×D = {failure['severity']}×{failure['occurrence']}×{failure['detection']} = **{rpn}**")

# Footer with live update indicator
st.divider()

# Calculate time metrics
time_since_last_fetch = time.time() - st.session_state.last_fetch_time
time_until_next_refresh = max(0, REFRESH_SECONDS - time_since_last_fetch)

# Display footer with real-time info
col_footer1, col_footer2, col_footer3 = st.columns([2, 2, 1])

with col_footer1:
    st.caption(f"◆ **Last updated:** {current_time.strftime('%Y-%m-%d %H:%M:%S')} | **Refresh:** #{st.session_state.refresh_counter}")

with col_footer2:
    if should_fetch_new_data:
        st.caption(f"✅ **Status:** Data Fresh | **Interval:** {REFRESH_SECONDS}s")
    else:
        st.caption(f"⏳ **Next refresh in:** {time_until_next_refresh:.1f}s | **Interval:** {REFRESH_SECONDS}s")

with col_footer3:
    if st.session_state.last_fetch_time > 0:
        st.caption(f"📊 **Cached:** {len(st.session_state.cached_components_data)}/{len(COMPONENTS)} components")

# Auto-refresh mechanism - check every 1 second
if not st.session_state.stop_pressed:
    time.sleep(1)  # Check every second instead of waiting full 5 seconds
    st.rerun()
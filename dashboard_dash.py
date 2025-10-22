

from __future__ import annotations

import os
import time
from typing import Dict, List, Tuple, Any
from datetime import datetime
from collections import deque

import pandas as pd
import requests

import dash
from dash import dcc, html, Input, Output, State, callback_context
import dash_bootstrap_components as dbc
import plotly.graph_objects as go
from plotly.subplots import make_subplots


# ====================================================================
# CONFIGURATION
# ====================================================================
API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:5000/api/health")
PREDICT_API_URL = os.getenv("PREDICT_API_URL", "http://localhost:5000/api/predict/maintenance")

COMPONENTS: List[str] = [
    "Pre-Feeder",
    "Feeder",
    "Printing",
    "Slotter",
    "Stacker",
]

REFRESH_SECONDS = int(os.getenv("REFRESH_SECONDS", "5"))
REQUEST_TIMEOUT = float(os.getenv("REQUEST_TIMEOUT", "12"))
MAX_RETRIES = int(os.getenv("MAX_RETRIES", "2"))

# FMEA Data (Static)
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

# Global storage for historical data (in production, use Redis or database)
class DataStore:
    def __init__(self):
        self.health_history = {comp: deque(maxlen=50) for comp in COMPONENTS}
        self.oee_history = deque(maxlen=50)
        self.overall_health_history = deque(maxlen=50)
        self.timestamps = deque(maxlen=50)
        self.machine_logs = deque(maxlen=20)
        self.cached_components_data = {}
        self.last_fetch_time = 0
        self.refresh_counter = 0

data_store = DataStore()


# ====================================================================
# HELPER FUNCTIONS
# ====================================================================

def format_number(val):
    """Format number with thousand separator"""
    if val is None:
        return "-"
    if isinstance(val, (int, float)):
        return f"{val:,.0f}"
    return str(val)


def format_percentage(val):
    """Format percentage value"""
    if val is None:
        return "-"
    try:
        return f"{float(val):.2f}%"
    except:
        return str(val)


def metric_card(title, value, delta=None, status="normal", error=None):
    """Create a metric card component"""
    # Determine color based on status
    color_map = {
        "normal": "success",
        "warning": "warning",
        "danger": "danger",
        "info": "info"
    }
    color = color_map.get(status, "secondary")
    
    if error:
        return dbc.Card([
            dbc.CardBody([
                html.H6(title, className="card-subtitle mb-2 text-muted"),
                html.H4("Error", className="card-title text-danger"),
                html.P(error, className="small text-muted")
            ])
        ], color="danger", outline=True, className="mb-3")
    
    card_content = [
        html.H6(title, className="card-subtitle mb-2 text-muted"),
        html.H3(value, className="card-title"),
    ]
    
    if delta is not None:
        delta_color = "success" if delta >= 0 else "danger"
        delta_icon = "↑" if delta >= 0 else "↓"
        card_content.append(
            html.P(
                f"{delta_icon} {abs(delta):.2f}%",
                className=f"text-{delta_color} mb-0"
            )
        )
    
    return dbc.Card([
        dbc.CardBody(card_content)
    ], color=color, outline=True, className="mb-3")


def fetch_health(component: str) -> Tuple[bool, dict | str]:
    """Fetch health info for a component from the Flask API with retry logic."""
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
        except requests.exceptions.ConnectionError as e:
            last_error = f"Connection error: {str(e)[:50]}"
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
        except requests.exceptions.HTTPError as e:
            return False, f"HTTP {e.response.status_code}: {e.response.text[:100]}"
        except requests.exceptions.RequestException as e:
            last_error = f"Request error: {str(e)[:50]}"
            if attempt < MAX_RETRIES - 1:
                time.sleep(1)
        except ValueError:
            return False, "Invalid JSON response"
    
    return False, last_error or "Unknown error"


def get_status_color(health_index: float) -> str:
    """Return status color based on health index"""
    if health_index >= 70:
        return "success"
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
        if isinstance(data, dict) and 'error' not in data:
            if 'health_index' in data and isinstance(data['health_index'], (int, float)):
                health_indices.append(data['health_index'])
            metrics = data.get('metrics', {})
            if 'oee_score' in metrics and isinstance(metrics['oee_score'], (int, float)):
                oee_values.append(metrics['oee_score'])
    
    overall_health = sum(health_indices) / len(health_indices) if health_indices else 0
    overall_oee = sum(oee_values) / len(oee_values) if oee_values else 0
    
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


def create_trend_chart() -> go.Figure:
    """Create trend chart for health index and OEE"""
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Overall Health Index Trend', 'OEE Trend'),
        vertical_spacing=0.15
    )
    
    timestamps = list(data_store.timestamps)
    
    # Health Index Trend
    if data_store.overall_health_history:
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=list(data_store.overall_health_history),
                mode='lines+markers',
                name='Health Index',
                line=dict(color='#2E86AB', width=3),
                fill='tozeroy',
                fillcolor='rgba(46, 134, 171, 0.2)'
            ),
            row=1, col=1
        )
    
    # OEE Trend
    if data_store.oee_history:
        fig.add_trace(
            go.Scatter(
                x=timestamps,
                y=list(data_store.oee_history),
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
        template='plotly_white',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_oee_components_chart(components_data: Dict) -> go.Figure:
    """Create OEE components breakdown chart"""
    fig = go.Figure()
    
    for component in COMPONENTS:
        data = components_data.get(component, {})
        if 'error' not in data:
            metrics = data.get('metrics', {})
            avail = metrics.get('availability_rate', 0)
            perf = metrics.get('performance_rate', 0)
            qual = metrics.get('quality_rate', 0)
            
            fig.add_trace(go.Bar(
                name=component,
                x=['Availability', 'Performance', 'Quality'],
                y=[avail, perf, qual],
                text=[f'{avail:.1f}%', f'{perf:.1f}%', f'{qual:.1f}%'],
                textposition='auto',
            ))
    
    fig.update_layout(
        title='OEE Components by Machine',
        xaxis_title='OEE Components',
        yaxis_title='Percentage (%)',
        barmode='group',
        height=400,
        yaxis=dict(range=[0, 100]),
        template='plotly_white',
        margin=dict(l=50, r=50, t=80, b=50)
    )
    
    return fig


def create_oee_gauge_chart(calculated_oee: float) -> go.Figure:
    """Create OEE gauge chart"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=calculated_oee,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Overall OEE"},
        delta={'reference': 85, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
        gauge={
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
    
    fig.update_layout(
        height=400,
        margin=dict(l=20, r=20, t=60, b=20)
    )
    
    return fig


# ====================================================================
# APP INITIALIZATION
# ====================================================================
external_stylesheets = [dbc.themes.BOOTSTRAP, dbc.icons.FONT_AWESOME]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)
app.title = "FlexoTwin Dashboard"
server = app.server  # Expose for deployment

# Custom CSS
app.index_string = '''
<!DOCTYPE html>
<html>
    <head>
        {%metas%}
        <title>{%title%}</title>
        {%favicon%}
        {%css%}
        <style>
            .status-healthy {
                background-color: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                margin: 20px 0;
            }
            .status-warning {
                background-color: #fff3cd;
                color: #856404;
                padding: 15px;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                margin: 20px 0;
            }
            .status-danger {
                background-color: #f8d7da;
                color: #721c24;
                padding: 15px;
                border-radius: 5px;
                text-align: center;
                font-weight: bold;
                margin: 20px 0;
            }
        </style>
    </head>
    <body>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
'''


# ====================================================================
# LAYOUT
# ====================================================================

def create_sidebar():
    """Create sidebar with controls and prediction module"""
    return dbc.Col([
        html.H4("▼ Dashboard Controls", className="mb-3"),
        
        # Auto-refresh interval display
        dbc.Card([
            dbc.CardBody([
                html.P([html.I(className="fas fa-sync-alt me-2"), f"Refresh: {REFRESH_SECONDS}s"], className="mb-1"),
                html.P([html.I(className="fas fa-server me-2"), "API: localhost:5000"], className="mb-1"),
                html.P([html.I(className="fas fa-database me-2"), "History: 50 points"], className="mb-0"),
            ])
        ], className="mb-3"),
        
        html.Hr(),
        
        # Prediction Module
        html.H4("🔧 Modul Prediksi Maintenance", className="mb-3"),
        html.P("Prediksi durasi maintenance berdasarkan data produksi", className="text-muted small"),
        
        dbc.Card([
            dbc.CardBody([
                dbc.Label("📦 Total Produksi (Pcs)"),
                dbc.Input(
                    id="input-total-produksi",
                    type="number",
                    value=10000,
                    min=0,
                    step=100,
                    className="mb-3"
                ),
                
                dbc.Label("❌ Produk Cacat (Pcs)"),
                dbc.Input(
                    id="input-produk-cacat",
                    type="number",
                    value=500,
                    min=0,
                    step=10,
                    className="mb-3"
                ),
                
                dbc.Button(
                    "🚀 Jalankan Prediksi",
                    id="btn-predict",
                    color="primary",
                    className="w-100 mb-3"
                ),
                
                html.Div(id="prediction-result")
            ])
        ], className="mb-3"),
        
        html.Hr(),
        
        # FMEA Selection
        html.H4("▼ FMEA Analysis", className="mb-3"),
        dbc.Select(
            id="fmea-component-select",
            options=[{"label": comp, "value": comp} for comp in COMPONENTS],
            value=COMPONENTS[0],
            className="mb-3"
        ),
        
    ], width=3, className="bg-light p-3", style={"height": "100vh", "overflowY": "auto"})


def create_main_content():
    """Create main dashboard content"""
    return dbc.Col([
        # Header
        html.Div([
            html.H1("⚙ FlexoTwin Digital Twin Dashboard", className="display-5 mb-2"),
            html.P("Smart Maintenance 4.0 - Real-Time Monitoring System", className="lead text-muted"),
        ], className="mb-4"),
        
        # Auto-refresh interval component
        dcc.Interval(
            id='interval-component',
            interval=REFRESH_SECONDS * 1000,
            n_intervals=0
        ),
        
        # Store components for data caching
        dcc.Store(id='cached-data-store'),
        
        # Section 1: Overall Metrics
        html.H2("▣ Ringkasan Kondisi Mesin", className="mb-3"),
        html.Div(id="overall-metrics-section"),
        html.Div(id="status-indicator-section"),
        html.Hr(),
        
        # Section 1.5: OEE Detail
        html.H2("▣ Komponen OEE Detail", className="mb-2"),
        html.H5("Overall Equipment Effectiveness (OEE) = Availability × Performance × Quality", className="text-muted mb-3"),
        html.Div(id="oee-components-section"),
        html.Div(id="oee-charts-section"),
        html.Div(id="oee-analysis-section"),
        html.Hr(),
        
        # Section 2: Component Status
        html.H2("▣ Status Kesehatan per Komponen", className="mb-3"),
        html.Div(id="components-status-section"),
        html.Hr(),
        
        # Section 3: Trends and Logs
        html.H2("▣ Grafik Tren dan Log Historis", className="mb-3"),
        dbc.Row([
            dbc.Col([
                html.H4("Tren Performa"),
                dcc.Graph(id="trend-chart")
            ], width=8),
            dbc.Col([
                html.H4("▣ Log Status Terakhir"),
                html.Div(id="logs-table")
            ], width=4),
        ]),
        html.Hr(),
        
        # Section 4: FMEA Analysis
        html.H2("▣ Analisis Akar Masalah (FMEA)", className="mb-3"),
        html.Div(id="fmea-section"),
        html.Hr(),
        
        # Footer
        html.Div(id="footer-section", className="text-muted small"),
        
    ], width=9, className="p-4", style={"height": "100vh", "overflowY": "auto"})


# Main Layout
app.layout = dbc.Container([
    dbc.Row([
        create_sidebar(),
        create_main_content()
    ])
], fluid=True, className="p-0")


# ====================================================================
# CALLBACKS
# ====================================================================

@app.callback(
    [
        Output("overall-metrics-section", "children"),
        Output("status-indicator-section", "children"),
        Output("oee-components-section", "children"),
        Output("oee-charts-section", "children"),
        Output("oee-analysis-section", "children"),
        Output("components-status-section", "children"),
        Output("trend-chart", "figure"),
        Output("logs-table", "children"),
        Output("fmea-section", "children"),
        Output("footer-section", "children"),
    ],
    [Input("interval-component", "n_intervals"),
     Input("fmea-component-select", "value")]
)
def update_dashboard(n_intervals, selected_fmea_component):
    """Main callback to update all dashboard sections"""
    
    # Increment refresh counter
    data_store.refresh_counter += 1
    current_time = time.time()
    
    # Fetch component data
    all_comps_data = []
    health_scores = []
    oee_list = []
    availability_list = []
    performance_list = []
    quality_list = []
    
    for comp in COMPONENTS:
        success, payload = fetch_health(comp)
        if success:
            all_comps_data.append((comp, payload))
            health = payload.get("health_index", 0)
            health_scores.append(health)
            
            # Extract OEE components
            availability_list.append(payload.get("availability_rate", 0))
            performance_list.append(payload.get("performance_rate", 0))
            quality_list.append(payload.get("quality_rate", 0))
            oee_list.append(payload.get("oee", 0))
            
            # Store in history
            data_store.health_history[comp].append(health)
        else:
            all_comps_data.append((comp, {"error": str(payload)}))
            health_scores.append(0)
    
    # Calculate overall metrics
    overall_health = sum(health_scores) / len(health_scores) if health_scores else 0
    overall_oee = sum(oee_list) / len(oee_list) if oee_list else 0
    overall_availability = sum(availability_list) / len(availability_list) if availability_list else 0
    overall_performance = sum(performance_list) / len(performance_list) if performance_list else 0
    overall_quality = sum(quality_list) / len(quality_list) if quality_list else 0
    
    # Store in history
    data_store.overall_health_history.append(overall_health)
    data_store.oee_history.append(overall_oee)
    data_store.timestamps.append(datetime.now())
    
    # ------------------------------------------------------------------
    # Section 1: Overall Metrics
    # ------------------------------------------------------------------
    overall_metrics = dbc.Row([
        dbc.Col(metric_card("Overall Health Index", f"{overall_health:.2f}%", status="normal"), width=3),
        dbc.Col(metric_card("Overall OEE", f"{overall_oee:.2f}%", status="info"), width=3),
        dbc.Col(metric_card("Availability", f"{overall_availability:.2f}%", status="info"), width=2),
        dbc.Col(metric_card("Performance", f"{overall_performance:.2f}%", status="info"), width=2),
        dbc.Col(metric_card("Quality", f"{overall_quality:.2f}%", status="info"), width=2),
    ])
    
    # Status indicator
    if overall_health >= 80:
        status_class = "status-healthy"
        status_text = "✅ Sistem dalam kondisi optimal"
    elif overall_health >= 60:
        status_class = "status-warning"
        status_text = "⚠️ Perhatian diperlukan pada beberapa komponen"
    else:
        status_class = "status-danger"
        status_text = "🚨 Tindakan segera diperlukan!"
    
    status_indicator = html.Div(status_text, className=status_class)
    
    # ------------------------------------------------------------------
    # Section 1.5: OEE Components Detail
    # ------------------------------------------------------------------
    oee_comp_cards = dbc.Row([
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("⏱ Availability Rate", className="card-title"),
                    html.H3(f"{overall_availability:.2f}%", className="text-primary"),
                    html.P("Waktu operasi efektif / Total waktu tersedia", className="small text-muted")
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("⚡ Performance Rate", className="card-title"),
                    html.H3(f"{overall_performance:.2f}%", className="text-success"),
                    html.P("Kecepatan aktual / Kecepatan ideal", className="small text-muted")
                ])
            ])
        ], width=4),
        dbc.Col([
            dbc.Card([
                dbc.CardBody([
                    html.H5("✅ Quality Rate", className="card-title"),
                    html.H3(f"{overall_quality:.2f}%", className="text-warning"),
                    html.P("Produk baik / Total produk", className="small text-muted")
                ])
            ])
        ], width=4),
    ])
    
    # OEE Charts
    oee_charts = dbc.Row([
        dbc.Col([
            dcc.Graph(
                figure=go.Figure(
                    data=[
                        go.Bar(name='Availability', x=COMPONENTS, y=availability_list, marker_color='#0d6efd'),
                        go.Bar(name='Performance', x=COMPONENTS, y=performance_list, marker_color='#198754'),
                        go.Bar(name='Quality', x=COMPONENTS, y=quality_list, marker_color='#ffc107'),
                    ],
                    layout=go.Layout(
                        title="OEE Components by Component",
                        barmode='group',
                        yaxis=dict(title="Percentage (%)", range=[0, 100]),
                        xaxis=dict(title="Component"),
                        height=400
                    )
                )
            )
        ], width=6),
        dbc.Col([
            dcc.Graph(
                figure=go.Figure(
                    data=[
                        go.Scatter(
                            x=list(range(len(data_store.oee_history))),
                            y=list(data_store.oee_history),
                            mode='lines+markers',
                            name='OEE',
                            line=dict(color='#0d6efd', width=3)
                        )
                    ],
                    layout=go.Layout(
                        title="OEE Trend (Last 50 Points)",
                        yaxis=dict(title="OEE (%)", range=[0, 100]),
                        xaxis=dict(title="Time Point"),
                        height=400
                    )
                )
            )
        ], width=6),
    ])
    
    # OEE Analysis
    oee_analysis = dbc.Alert([
        html.H5("📊 Analisis OEE", className="alert-heading"),
        html.P(f"OEE saat ini: {overall_oee:.2f}% (A: {overall_availability:.2f}% × P: {overall_performance:.2f}% × Q: {overall_quality:.2f}%)"),
        html.Hr(),
        html.P([
            html.Strong("Rekomendasi: "),
            "OEE optimal adalah > 85%. " if overall_oee >= 85 else
            f"Fokuskan perbaikan pada {'Availability' if overall_availability == min(overall_availability, overall_performance, overall_quality) else 'Performance' if overall_performance == min(overall_availability, overall_performance, overall_quality) else 'Quality'} untuk meningkatkan OEE."
        ], className="mb-0")
    ], color="info" if overall_oee >= 85 else "warning")
    
    # ------------------------------------------------------------------
    # Section 2: Component Status
    # ------------------------------------------------------------------
    component_cards = []
    for comp, payload in all_comps_data:
        if "error" in payload:
            card = metric_card(title=comp, value="-", error=payload.get("error", "Unknown error"))
        else:
            health = payload.get("health_index", 0)
            if health >= 80:
                status = "normal"
            elif health >= 60:
                status = "warning"
            else:
                status = "danger"
            
            value_txt = f"{health:.2f}%"
            card = metric_card(title=comp, value=value_txt, delta=None, status=status)
        
        component_cards.append(dbc.Col(card, width=12 // len(COMPONENTS)))
    
    components_section = dbc.Row(component_cards)
    
    # ------------------------------------------------------------------
    # Section 3: Trends and Logs
    # ------------------------------------------------------------------
    # Trend chart
    trend_fig = go.Figure()
    for comp in COMPONENTS:
        if len(data_store.health_history[comp]) > 0:
            trend_fig.add_trace(go.Scatter(
                x=list(range(len(data_store.health_history[comp]))),
                y=list(data_store.health_history[comp]),
                mode='lines+markers',
                name=comp
            ))
    
    trend_fig.update_layout(
        title="Component Health Trends",
        xaxis_title="Time Point",
        yaxis_title="Health Index (%)",
        yaxis=dict(range=[0, 100]),
        height=400,
        hovermode='x unified'
    )
    
    # Logs table
    logs_rows = []
    for comp, payload in all_comps_data[:5]:  # Show last 5
        if "error" not in payload:
            health = payload.get("health_index", 0)
            color = "success" if health >= 80 else "warning" if health >= 60 else "danger"
            logs_rows.append(
                html.Tr([
                    html.Td(comp),
                    html.Td(f"{health:.2f}%", className=f"text-{color} fw-bold"),
                ])
            )
    
    logs_table = dbc.Table([
        html.Thead(html.Tr([html.Th("Component"), html.Th("Health")])),
        html.Tbody(logs_rows)
    ], bordered=True, hover=True, size="sm")
    
    # ------------------------------------------------------------------
    # Section 4: FMEA Analysis
    # ------------------------------------------------------------------
    selected_fmea = FMEA_DATA.get(selected_fmea_component, {})
    fmea_rows = []
    for failure in selected_fmea.get("failures", []):
        rpn = failure["severity"] * failure["occurrence"] * failure["detection"]
        fmea_rows.append(html.Tr([
            html.Td(failure["mode"]),
            html.Td(failure["cause"]),
            html.Td(failure["effect"]),
            html.Td(failure["severity"], className="text-center"),
            html.Td(failure["occurrence"], className="text-center"),
            html.Td(failure["detection"], className="text-center"),
            html.Td(rpn, className="text-center fw-bold text-danger" if rpn > 250 else "text-center"),
        ]))
    
    fmea_table = dbc.Table([
        html.Thead(html.Tr([
            html.Th("Failure Mode"),
            html.Th("Root Cause"),
            html.Th("Effect"),
            html.Th("S", className="text-center"),
            html.Th("O", className="text-center"),
            html.Th("D", className="text-center"),
            html.Th("RPN", className="text-center"),
        ])),
        html.Tbody(fmea_rows)
    ], bordered=True, hover=True, responsive=True)
    
    fmea_section = html.Div([
        dbc.Alert(f"🔍 Component: {selected_fmea_component} | RPN Score: {selected_fmea.get('RPN', 0)}", color="secondary"),
        fmea_table
    ])
    
    # ------------------------------------------------------------------
    # Footer
    # ------------------------------------------------------------------
    footer = html.P(
        f"Last refresh: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Refresh #{data_store.refresh_counter} | API: {API_BASE_URL}",
        className="text-center"
    )
    
    return (
        overall_metrics,
        status_indicator,
        oee_comp_cards,
        oee_charts,
        oee_analysis,
        components_section,
        trend_fig,
        logs_table,
        fmea_section,
        footer
    )


@app.callback(
    Output("prediction-result", "children"),
    [Input("btn-predict", "n_clicks")],
    [State("input-total-produksi", "value"),
     State("input-produk-cacat", "value")]
)
def run_prediction(n_clicks, total_produksi, produk_cacat):
    """Run maintenance duration prediction"""
    if not n_clicks:
        return html.Div()
    
    if total_produksi is None or produk_cacat is None:
        return dbc.Alert("⚠️ Mohon isi semua input!", color="warning")
    
    try:
        # Call prediction API
        response = requests.post(
            PREDICT_API_URL,
            json={
                "total_produksi": int(total_produksi),
                "produk_cacat": int(produk_cacat)
            },
            timeout=10
        )
        response.raise_for_status()
        data = response.json()
        
        prediction_minutes = data.get("prediction", 0)
        prediction_formatted = data.get("prediction_formatted", f"{prediction_minutes:.2f} menit")
        
        # Determine alert color
        if prediction_minutes < 30:
            alert_color = "success"
            icon = "✅"
        elif prediction_minutes < 60:
            alert_color = "warning"
            icon = "⚠️"
        else:
            alert_color = "danger"
            icon = "🚨"
        
        return dbc.Alert([
            html.H5(f"{icon} Hasil Prediksi", className="alert-heading"),
            html.P(f"Durasi Maintenance: {prediction_formatted}", className="mb-2"),
            html.Hr(),
            html.P(f"Input: {format_number(total_produksi)} pcs produksi, {format_number(produk_cacat)} pcs cacat", className="small mb-0")
        ], color=alert_color)
        
    except Exception as e:
        return dbc.Alert(f"❌ Error: {str(e)}", color="danger")


# ====================================================================
# MAIN ENTRY POINT
# ====================================================================
if __name__ == "__main__":
    print("=" * 70)
    print("🚀 FlexoTwin Dashboard (Dash Framework)")
    print("=" * 70)
    print(f"API Base URL: {API_BASE_URL}")
    print(f"Refresh Interval: {REFRESH_SECONDS} seconds")
    print(f"Components: {', '.join(COMPONENTS)}")
    print("=" * 70)
    print("Starting dashboard on http://localhost:8050")
    print("=" * 70)
    
    app.run(debug=True, host="0.0.0.0", port=8050)


# -----------------------------
# Callbacks
# -----------------------------
@app.callback(
    Output("cards-container", "children"),
    Input("interval", "n_intervals")
)
def update_cards(_n: int):
    """Update all component cards on every interval tick."""
    row_cols = []

    for comp in COMPONENTS:
        ok, payload = fetch_health(comp)
        if ok:
            hi = payload.get("health_index")
            status = payload.get("status")
            # Format like st.metric: value with 2 decimals
            value_txt = "-" if hi is None else f"{float(hi):.2f}"
            # Optional: map health index to quick delta or badge text
            card = metric_card(title=comp, value=value_txt, delta=None, status=status)
        else:
            card = metric_card(title=comp, value="-", error=payload.get("error", "Unknown error"))

        col = dbc.Col(card, xs=12, sm=6, md=4, lg=3, className="mb-4")
        row_cols.append(col)

    # Arrange cards in a responsive grid
    return [dbc.Row(row_cols)]


# -----------------------------
# Main
# -----------------------------
if __name__ == "__main__":
    # For local development; for production, rely on WSGI server using `server`
    app.run_server(debug=True, host="0.0.0.0", port=int(os.getenv("PORT", "8050")))

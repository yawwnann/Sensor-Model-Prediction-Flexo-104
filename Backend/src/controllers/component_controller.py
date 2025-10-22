"""
Component Controller
Endpoints untuk manajemen komponen
"""

from flask import Blueprint, jsonify
from src.services.database_service import db_service
from src.services.health_service import HealthService
from src.utils.logger import get_logger

# Setup
component_bp = Blueprint('components', __name__, url_prefix='/api')
logger = get_logger(__name__)
health_service = HealthService()


@component_bp.route('/components', methods=['GET'])
def get_all_components():
    """
    Endpoint untuk mendapatkan daftar semua komponen.
    
    Returns:
        JSON response dengan list semua komponen dan RPN values
    """
    logger.info("All components requested")
    
    try:
        # Ambil data dari database
        results = db_service.get_all_components()
        
        if results is None:
            logger.error("Database connection failed")
            return jsonify({
                "error": "Koneksi database gagal",
                "message": "Tidak dapat terhubung ke database. Periksa koneksi internet dan konfigurasi DATABASE_URL.",
                "troubleshooting": [
                    "Periksa koneksi internet",
                    "Verifikasi DATABASE_URL di file .env",
                    "Pastikan database server dapat diakses"
                ]
            }), 503
        
        # Format hasil
        components = []
        for row in results:
            component_data = {
                "id": row[0],
                "name": row[1],
                "rpn_value": row[2],
                "health_endpoint": f"/api/health/{row[1]}",
                "details_endpoint": f"/api/components/{row[1]}/health"
            }
            components.append(component_data)
        
        response = {
            "components": components,
            "total_count": len(components),
            "metadata": {
                "source": "PostgreSQL Database",
                "last_updated": "Real-time",
                "available_operations": [
                    "GET /api/health/<component_name>",
                    "GET /api/components/<component_name>/health"
                ]
            }
        }
        
        logger.info(f"Successfully retrieved {len(components)} components")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error retrieving components: {e}")
        return jsonify({
            "error": "Error mengambil data komponen",
            "message": str(e),
            "debug_info": {
                "endpoint": "/api/components",
                "method": "GET"
            }
        }), 500


@component_bp.route('/components/<component_name>/health', methods=['GET'])
def get_component_detailed_health(component_name: str):
    """
    Endpoint untuk mendapatkan detail lengkap kesehatan komponen.
    
    Args:
        component_name: Nama komponen dari URL path
        
    Returns:
        JSON response dengan detail lengkap kesehatan komponen
    """
    logger.info(f"Detailed health requested for component: {component_name}")
    
    try:
        # Ambil data RPN dari database
        rpn_value, rpn_max = db_service.get_component_rpn(component_name)
        
        if rpn_value is None:
            logger.warning(f"Component not found: {component_name}")
            return jsonify({
                "error": "Komponen tidak ditemukan",
                "component": component_name,
                "message": f"Komponen '{component_name}' tidak ada di database",
                "suggestion": "Gunakan GET /api/components untuk melihat daftar komponen yang tersedia"
            }), 404
        
        # Hitung health metrics
        health_data = health_service.calculate_component_health(rpn_value, rpn_max)
        
        # Format response dengan detail lengkap
        response = {
            "component": {
                "name": component_name,
                "rpn_value": health_data["rpn_value"],
                "rpn_max": health_data["rpn_max"],
                "rpn_percentage": round((health_data["rpn_value"] / health_data["rpn_max"]) * 100, 2)
            },
            "health_assessment": {
                "overall_index": health_data["final_health_index"],
                "status": health_data["status"],
                "color_code": health_service.get_health_color(health_data["final_health_index"]),
                "description": health_service.get_health_description(health_data["final_health_index"]),
                "severity_level": health_service.get_severity_level(health_data["final_health_index"])
            },
            "detailed_metrics": {
                "rpn_score": {
                    "value": health_data["rpn_score"],
                    "weight": 0.4,
                    "description": "Risk Priority Number Score",
                    "interpretation": "Semakin tinggi semakin baik (risiko rendah)"
                },
                "oee_score": {
                    "value": health_data["oee_score"],
                    "weight": 0.6,
                    "description": "Overall Equipment Effectiveness Score",
                    "interpretation": "Efektivitas operasional mesin"
                }
            },
            "calculation": {
                "formula": "(RPN_Score × 0.4) + (OEE_Score × 0.6)",
                "breakdown": f"({health_data['rpn_score']} × 0.4) + ({health_data['oee_score']} × 0.6) = {health_data['final_health_index']}",
                "weights_explanation": {
                    "rpn_weight": "40% - Faktor risiko dan keandalan",
                    "oee_weight": "60% - Faktor efisiensi operasional"
                }
            },
            "recommendations": health_service.get_recommendations(health_data["final_health_index"]),
            "metadata": {
                "calculation_timestamp": health_service.get_current_timestamp(),
                "data_source": "Real-time database + simulated OEE",
                "refresh_interval": "Real-time (setiap request)"
            }
        }
        
        logger.info(f"Detailed health calculated for {component_name}: {health_data['final_health_index']}")
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting detailed health for {component_name}: {e}")
        return jsonify({
            "error": "Error mengambil detail kesehatan komponen",
            "component": component_name,
            "message": str(e)
        }), 500
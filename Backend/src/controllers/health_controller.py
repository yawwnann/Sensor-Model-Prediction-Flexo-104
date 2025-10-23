"""
Health Controller
Endpoints untuk health check API dan komponen
"""

from flask import Blueprint, jsonify
from src.services.database_service import db_service
from src.services.health_service import HealthService
from src.utils.logger import get_logger, log_success, log_error, log_metric
from config import APP_NAME, APP_VERSION

# Setup
health_bp = Blueprint('health', __name__)
logger = get_logger(__name__)
health_service = HealthService()


@health_bp.route('/health', methods=['GET'])
def api_health_check():
    """
    Endpoint untuk health check umum API.
    
    Returns:
        JSON response dengan status server
    """
    logger.info("API health check requested")
    
    try:
        # Test database connection
        db_status = db_service.test_connection()
        
        response_data = {
            "status": "API Server Running",
            "service": APP_NAME,
            "version": APP_VERSION,
            "database": {
                "type": "PostgreSQL (Supabase)",
                "status": "Connected" if db_status else "Disconnected"
            },
            "endpoints_available": [
                "GET /api/health",
                "GET /api/health/<component_name>",
                "GET /api/components",
                "GET /api/components/<component_name>/health",
                "POST /api/predict/maintenance",
                "POST /api/predict/maintenance/batch",
                "GET /api/model/info",
                "GET /api/docs"
            ]
        }
        
        status_code = 200 if db_status else 503
        
        logger.info(f"API health check completed - Status: {status_code}")
        return jsonify(response_data), status_code
        
    except Exception as e:
        logger.error(f"Error in API health check: {e}")
        return jsonify({
            "status": "API Server Running with Errors",
            "service": APP_NAME,
            "version": APP_VERSION,
            "error": str(e)
        }), 500


@health_bp.route('/health/<component_name>', methods=['GET'])
def get_component_health(component_name: str):
    """
    Endpoint untuk mendapatkan status kesehatan komponen tertentu.
    
    Args:
        component_name: Nama komponen dari URL path
        
    Returns:
        JSON response dengan health metrics komponen
    """
    logger.info(f"[REQUEST] Health check requested for: {component_name}")
    
    try:
        # Ambil data RPN dari database
        rpn_value, rpn_max = db_service.get_component_rpn(component_name)
        
        # Jika komponen tidak ditemukan
        if rpn_value is None:
            log_error(logger, f"Component not found: {component_name}")
            return jsonify({
                "error": "Komponen tidak ditemukan",
                "component": component_name,
                "message": f"Komponen '{component_name}' tidak ada di database",
                "available_endpoints": [
                    "GET /api/components - untuk melihat semua komponen"
                ]
            }), 404
        
        # Hitung health metrics dengan nama komponen
        health_data = health_service.calculate_component_health(component_name, rpn_value, rpn_max)
        
        # Log metrics dengan format yang rapi
        logger.info(f"[CALCULATED] Health metrics calculated for {component_name}:")
        log_metric(logger, "RPN Score", f"{health_data['rpn_score']:.2f}", "%")
        log_metric(logger, "OEE Score", f"{health_data['oee_score']:.2f}", "%")
        log_metric(logger, "Health Index", f"{health_data['final_health_index']:.2f}", "%")
        log_metric(logger, "Status", health_data['status'])
        log_metric(logger, "Recommendations", f"{len(health_data['recommendations'])} items")
        
        # Format response
        response = {
            "component_name": component_name,
            "health_index": health_data["final_health_index"],
            "status": health_data["status"],
            "color": health_service.get_health_color(health_data["final_health_index"]),
            "description": health_service.get_health_description(health_data["final_health_index"]),
            "recommendations": health_data["recommendations"],  # Rekomendasi berbasis FMEA
            "metrics": {
                "rpn_score": health_data["rpn_score"],
                "oee_score": health_data["oee_score"],
                "availability_rate": health_data["availability_rate"],
                "performance_rate": health_data["performance_rate"],
                "quality_rate": health_data["quality_rate"],
                "rpn_value": health_data["rpn_value"],
                "rpn_max": health_data["rpn_max"]
            },
            "calculation_details": {
                "formula": "(RPN_Score × 0.4) + (OEE_Score × 0.6)",
                "weights": {
                    "rpn_weight": 0.4,
                    "oee_weight": 0.6
                }
            }
        }
        
        # Tambahkan informasi auto-prediction jika tersedia
        if "auto_prediction" in health_data:
            response["auto_prediction"] = health_data["auto_prediction"]
            logger.warning(f" Auto-prediction included in response for {component_name}")
        
        return jsonify(response), 200
        
    except Exception as e:
        log_error(logger, f"Error calculating component health for {component_name}: {e}")
        return jsonify({
            "error": "Error menghitung health komponen",
            "component": component_name,
            "message": str(e)
        }), 500
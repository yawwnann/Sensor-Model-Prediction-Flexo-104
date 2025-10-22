"""
routes.py
API Routes dan Endpoints
"""

from flask import Blueprint, jsonify
from .utils.logger import get_logger
from .services.mqtt_service import (
    get_latest_sensor_data,
    get_sensor_data_history,
    get_mqtt_client
)


# ============================================================================
# LOGGING
# ============================================================================

logger = get_logger(__name__)


# ============================================================================
# BLUEPRINT CREATION
# ============================================================================

api_bp = Blueprint('api', __name__, url_prefix='/api')


# ============================================================================
# SENSOR DATA ENDPOINTS
# ============================================================================

@api_bp.route('/sensor/latest', methods=['GET'])
def get_latest_sensor():
    """
    Endpoint untuk mendapatkan data sensor terbaru dari MQTT.
    
    Return:
    - JSON response dengan data sensor terbaru
    """
    
    logger.info("[API] GET /api/sensor/latest")
    
    try:
        data = get_latest_sensor_data()
        
        if data['machine_id'] is None:
            return jsonify({
                "error": "No data available",
                "message": "Sensor data has not been received yet"
            }), 204
        
        return jsonify({
            "success": True,
            "data": data
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting latest sensor data: {e}")
        return jsonify({
            "error": "Internal Server Error",
            "message": str(e)
        }), 500


@api_bp.route('/sensor/history', methods=['GET'])
def get_sensor_history():
    """
    Endpoint untuk mendapatkan history data sensor.
    
    Query Parameters:
    - limit: Jumlah data yang ingin diambil (default: 50)
    
    Return:
    - JSON response dengan history data sensor
    """
    
    from flask import request
    
    logger.info("[API] GET /api/sensor/history")
    
    try:
        limit = request.args.get('limit', default=50, type=int)
        
        # Validasi limit
        if limit < 1 or limit > 1000:
            limit = 50
        
        history = get_sensor_data_history(limit=limit)
        
        return jsonify({
            "success": True,
            "count": len(history),
            "limit": limit,
            "data": history
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting sensor history: {e}")
        return jsonify({
            "error": "Internal Server Error",
            "message": str(e)
        }), 500


@api_bp.route('/sensor/status', methods=['GET'])
def get_sensor_status():
    """
    Endpoint untuk mendapatkan status sensor dan MQTT connection.
    
    Return:
    - JSON response dengan status sensor
    """
    
    logger.info("[API] GET /api/sensor/status")
    
    try:
        mqtt_client = get_mqtt_client()
        latest_data = get_latest_sensor_data()
        
        return jsonify({
            "success": True,
            "mqtt": {
                "connected": mqtt_client.is_connected_to_broker() if mqtt_client else False,
                "broker": "broker.hivemq.com:1883",
                "topic": "flexotwin/machine/status"
            },
            "sensor": {
                "machine_id": latest_data.get('machine_id'),
                "status": latest_data.get('machine_status'),
                "last_update": latest_data.get('timestamp')
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting sensor status: {e}")
        return jsonify({
            "error": "Internal Server Error",
            "message": str(e)
        }), 500


# ============================================================================
# HEALTH & INFO ENDPOINTS
# ============================================================================

@api_bp.route('/info', methods=['GET'])
def get_api_info():
    """
    Endpoint untuk mendapatkan informasi API.
    
    Return:
    - JSON response dengan informasi API
    """
    
    logger.info("[API] GET /api/info")
    
    return jsonify({
        "service": "FlexoTwin Backend API",
        "version": "1.0.0",
        "description": "Backend API untuk sistem monitoring kesehatan mesin Flexo",
        "endpoints": {
            "sensor": {
                "latest": "GET /api/sensor/latest",
                "history": "GET /api/sensor/history?limit=50",
                "status": "GET /api/sensor/status"
            },
            "health": "GET /health"
        }
    }), 200


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@api_bp.errorhandler(404)
def not_found(error):
    """Handler untuk 404 Not Found"""
    return jsonify({
        "error": "Not Found",
        "message": "The requested endpoint was not found"
    }), 404


@api_bp.errorhandler(500)
def internal_error(error):
    """Handler untuk 500 Internal Server Error"""
    logger.error(f"API error: {error}")
    return jsonify({
        "error": "Internal Server Error",
        "message": "An unexpected error occurred"
    }), 500

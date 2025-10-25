"""
Sensor Controller
Controller untuk endpoint sensor data real-time
"""

from flask import Blueprint, jsonify, request
from src.services.database_service import db_service
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Create blueprint
sensor_bp = Blueprint('sensor', __name__)


@sensor_bp.route('/sensor/realtime', methods=['GET'])
def get_realtime_sensor_data():
    """
    GET /api/sensor/realtime
    
    Mengambil data sensor real-time langsung dari machine_logs.
    
    Query Parameters:
    - limit: Maksimal jumlah records (default: 20)
    
    Returns:
    - JSON dengan list sensor data real-time
    """
    try:
        # Ambil query parameters
        limit = request.args.get('limit', default=10, type=int)
        
        # Validasi limit
        if limit < 1 or limit > 50:
            limit = 10
        
        logger.info(f"[API] GET /api/sensor/realtime - limit={limit}")
        
        # Ambil data sensor real-time dari database
        with db_service.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        timestamp,
                        machine_status,
                        performance_rate,
                        quality_rate,
                        availability_rate,
                        cumulative_production,
                        cumulative_defects
                    FROM machine_logs
                    ORDER BY timestamp DESC
                    LIMIT %s
                """
                
                cursor.execute(query, [limit])
                results = cursor.fetchall()
                
                sensor_data = []
                for row in results:
                    timestamp, machine_status, performance_rate, quality_rate, availability_rate, cumulative_production, cumulative_defects = row
                    
                    # Hitung interval production dan defects (dari record sebelumnya)
                    interval_production = 0
                    interval_defects = 0
                    
                    # Ambil record sebelumnya untuk menghitung interval
                    if len(results) > 1:
                        prev_row = results[1] if len(results) > 1 else None
                        if prev_row:
                            prev_cumulative_production = prev_row[4] or 0
                            prev_cumulative_defects = prev_row[5] or 0
                            interval_production = max(0, cumulative_production - prev_cumulative_production)
                            interval_defects = max(0, cumulative_defects - prev_cumulative_defects)
                    
                    # Hitung defect rate
                    defect_rate = 0
                    if cumulative_production > 0:
                        defect_rate = (cumulative_defects / cumulative_production) * 100
                    
                    # Status icon
                    status_icon = "🟢" if machine_status == "Running" else "🔴"
                    
                    sensor_record = {
                        "id": f"SENSOR-{int(timestamp.timestamp() * 1000) % 100000}",
                        "timestamp": timestamp.isoformat(),
                        "machine_id": "C_FL104",
                        "machine_status": machine_status,
                        "performance_rate": round(performance_rate, 2),
                        "quality_rate": round(quality_rate, 2),
                        "availability_rate": round(availability_rate, 2),  # ✅ TAMBAHAN
                        "cumulative_production": cumulative_production,
                        "cumulative_defects": cumulative_defects,
                        "defect_rate": round(defect_rate, 2),
                        "status_icon": status_icon,
                        "interval_production": interval_production,
                        "interval_defects": interval_defects
                    }
                    
                    sensor_data.append(sensor_record)
        
        return jsonify({
            "success": True,
            "count": len(sensor_data),
            "data": sensor_data,
            "machine_id": "C_FL104",
            "last_updated": sensor_data[0]["timestamp"] if sensor_data else None
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_realtime_sensor_data: {e}")
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": str(e)
        }), 500


@sensor_bp.route('/sensor/current', methods=['GET'])
def get_current_sensor_status():
    """
    GET /api/sensor/current
    
    Mengambil status sensor terkini (record terakhir).
    
    Returns:
    - JSON dengan status sensor terkini
    """
    try:
        logger.info("[API] GET /api/sensor/current")
        
        # Ambil record terakhir dari database
        with db_service.get_connection() as conn:
            with conn.cursor() as cursor:
                query = """
                    SELECT 
                        timestamp,
                        machine_status,
                        performance_rate,
                        quality_rate,
                        availability_rate,
                        cumulative_production,
                        cumulative_defects
                    FROM machine_logs
                    ORDER BY timestamp DESC
                    LIMIT 2
                """
                
                cursor.execute(query)
                results = cursor.fetchall()
                
                if not results:
                    return jsonify({
                        "success": False,
                        "error": "No sensor data found"
                    }), 404
                
                # Current record (terbaru)
                current = results[0]
                timestamp, machine_status, performance_rate, quality_rate, availability_rate, cumulative_production, cumulative_defects = current
                
                # Hitung interval production dari record sebelumnya
                interval_production = 0
                if len(results) > 1:
                    prev = results[1]
                    prev_cumulative_production = prev[4] or 0
                    interval_production = max(0, cumulative_production - prev_cumulative_production)
                
                # Hitung defect rate
                defect_rate = 0
                if cumulative_production > 0:
                    defect_rate = (cumulative_defects / cumulative_production) * 100
                
                # Status icon
                status_icon = "🟢" if machine_status == "Running" else "🔴"
                
                current_status = {
                    "timestamp": timestamp.isoformat(),
                    "machine_id": "C_FL104",
                    "machine_status": machine_status,
                    "performance_rate": round(performance_rate, 2),
                    "quality_rate": round(quality_rate, 2),
                    "availability_rate": round(availability_rate, 2),  # ✅ TAMBAHAN
                    "cumulative_production": cumulative_production,
                    "cumulative_defects": cumulative_defects,
                    "defect_rate": round(defect_rate, 2),
                    "status_icon": status_icon,
                    "interval_production": interval_production
                }
        
        return jsonify({
            "success": True,
            "data": current_status
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_current_sensor_status: {e}")
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": str(e)
        }), 500
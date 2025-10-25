"""
Downtime Controller
Controller untuk endpoint downtime history dan statistics
"""

from flask import Blueprint, jsonify, request
from src.services.downtime_service import downtime_service
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Create blueprint
downtime_bp = Blueprint('downtime', __name__)


@downtime_bp.route('/downtime/history', methods=['GET'])
def get_downtime_history():
    """
    GET /api/downtime/history
    
    Mengambil history downtime dari machine_logs.
    
    Query Parameters:
    - limit: Maksimal jumlah events (default: 50)
    - component: Filter berdasarkan komponen (optional, default: all)
    - start_date: Filter tanggal mulai (format: YYYY-MM-DD)
    - end_date: Filter tanggal akhir (format: YYYY-MM-DD)
    
    Returns:
    - JSON dengan list downtime events
    """
    try:
        # Ambil query parameters
        limit = request.args.get('limit', default=50, type=int)
        component = request.args.get('component', default=None, type=str)
        start_date = request.args.get('start_date', default=None, type=str)
        end_date = request.args.get('end_date', default=None, type=str)
        
        # Validasi limit
        if limit < 1 or limit > 500:
            limit = 50
        
        logger.info(
            f"[API] GET /api/downtime/history - "
            f"limit={limit}, component={component}, "
            f"start_date={start_date}, end_date={end_date}"
        )
        
        # Ambil downtime history dari service
        downtime_events = downtime_service.get_downtime_history(
            limit=limit,
            component_filter=component,
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            "success": True,
            "count": len(downtime_events),
            "data": downtime_events,
            "filters": {
                "limit": limit,
                "component": component or "all",
                "start_date": start_date,
                "end_date": end_date
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_downtime_history: {e}")
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": str(e)
        }), 500


@downtime_bp.route('/downtime/statistics', methods=['GET'])
def get_downtime_statistics():
    """
    GET /api/downtime/statistics
    
    Mengambil statistik downtime (agregasi data).
    
    Query Parameters:
    - start_date: Filter tanggal mulai (format: YYYY-MM-DD)
    - end_date: Filter tanggal akhir (format: YYYY-MM-DD)
    
    Returns:
    - JSON dengan statistik downtime
    """
    try:
        # Ambil query parameters
        start_date = request.args.get('start_date', default=None, type=str)
        end_date = request.args.get('end_date', default=None, type=str)
        
        logger.info(
            f"[API] GET /api/downtime/statistics - "
            f"start_date={start_date}, end_date={end_date}"
        )
        
        # Ambil statistik dari service
        statistics = downtime_service.get_downtime_statistics(
            start_date=start_date,
            end_date=end_date
        )
        
        return jsonify({
            "success": True,
            "data": statistics,
            "filters": {
                "start_date": start_date,
                "end_date": end_date
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Error in get_downtime_statistics: {e}")
        return jsonify({
            "success": False,
            "error": "Internal Server Error",
            "message": str(e)
        }), 500

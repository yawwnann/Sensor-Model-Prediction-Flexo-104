"""
app.py
Main Flask Application Entry Point
FlexoTwin Smart Maintenance 4.0 - Backend API
"""

import signal
import sys
import os
import logging
from flask import Flask, jsonify
from src.utils.logger import get_logger, log_section, log_success, log_error, log_warning
from src.services.mqtt_service import initialize_mqtt, get_mqtt_client
from src.controllers.routes import register_routes


# Hanya inisialisasi logger sekali (hindari duplikasi di Flask debug mode)
logger = get_logger(__name__)

# ============================================================================
# DISABLE FLASK DEBUG LOGGING TO PREVENT DUPLICATES
# ============================================================================
# Suppress Flask's Werkzeug logger yang sering menyebabkan duplikasi log
werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.WARNING)

# Suppress Flask's development server verbose logging
flask_logger = logging.getLogger('flask.app')
flask_logger.setLevel(logging.WARNING)


def create_app():
    """
    Factory function untuk membuat dan mengkonfigurasi Flask application.
    
    Return:
    - app: Flask application instance
    """
    
    # Check if running in debug mode with reloader
    is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    is_first_time = not os.environ.get('WERKZEUG_RUN_MAIN')
    
    # Only show initialization logs on first run (not during reloader)
    if is_first_time:
        log_section(logger, "INITIALIZING FLEXOTWIN BACKEND APPLICATION")
    
    app = Flask(__name__)
    
    # ========================================================================
    # CONFIGURE FLASK DEBUG MODE LOGGING
    # ========================================================================
    # Set Flask configuration
    app.config['ENV'] = os.getenv('FLASK_ENV', 'development')
    app.config['DEBUG'] = app.config['ENV'] == 'development'
    
    # Further suppress logging in debug mode
    if app.config['DEBUG']:
        werkzeug_logger = logging.getLogger('werkzeug')
        werkzeug_logger.setLevel(logging.ERROR)
    
    log_success(logger, "Flask application created")
    
    logger.info("Registering blueprints...")
    register_routes(app)
    log_success(logger, "All blueprints registered")
    
    logger.info("Initializing MQTT service...")
    try:
        mqtt_client = initialize_mqtt()
        log_success(logger, "MQTT service initialized and started in background")
    except Exception as e:
        log_error(logger, f"Error initializing MQTT service: {e}")
        log_warning(logger, "Application will continue without MQTT service")
    
    # ========================================================================
    # HEALTH CHECK ENDPOINT
    # ========================================================================
    @app.route('/health', methods=['GET'])
    def health_check():
        """
        Health check endpoint untuk memverifikasi aplikasi berjalan.
        """
        
        mqtt_client = get_mqtt_client()
        
        return jsonify({
            "status": "healthy",
            "service": "FlexoTwin Backend API",
            "version": "1.0.0",
            "mqtt_connected": mqtt_client.is_connected_to_broker() if mqtt_client else False
        }), 200
    
    # ========================================================================
    # ERROR HANDLERS
    # ========================================================================
    @app.errorhandler(404)
    def not_found(error):
        """Handler untuk 404 Not Found"""
        return jsonify({
            "error": "Not Found",
            "message": "The requested resource was not found"
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handler untuk 500 Internal Server Error"""
        logger.error(f"Internal server error: {error}")
        return jsonify({
            "error": "Internal Server Error",
            "message": "An unexpected error occurred"
        }), 500
    
    if is_first_time:
        log_success(logger, "Application initialization complete")
    
    return app


def shutdown_handler(signum, frame):
    """
    Signal handler untuk graceful shutdown.
    Dipanggil saat menerima SIGINT (Ctrl+C) atau SIGTERM.
    """
    log_section(logger, "SHUTDOWN SIGNAL RECEIVED")
    
    try:
        mqtt_client = get_mqtt_client()
        if mqtt_client:
            mqtt_client.stop()
            log_success(logger, "MQTT client stopped")
    except Exception as e:
        log_error(logger, f"Error stopping MQTT client: {e}")
    
    log_success(logger, "Application shutdown complete")
    sys.exit(0)


if __name__ == '__main__':
    """
    Menjalankan aplikasi Flask dalam mode development.
    
    Notes:
    - Pengecekan WERKZEUG_RUN_MAIN memastikan log tidak duplikat di debug mode
    - Pada Flask debug mode dengan reloader, kode dijalankan 2x:
      1. First run: untuk reloader parent process (WERKZEUG_RUN_MAIN tidak ada)
      2. Second run: untuk actual server (WERKZEUG_RUN_MAIN='true')
    """
    
    app = create_app()
    
    # Register signal handlers untuk graceful shutdown
    signal.signal(signal.SIGINT, shutdown_handler)
    signal.signal(signal.SIGTERM, shutdown_handler)
    
    # Hanya tampilkan startup message saat main server process (bukan reloader parent)
    is_reloader_process = os.environ.get('WERKZEUG_RUN_MAIN') == 'true'
    is_first_time = not os.environ.get('WERKZEUG_RUN_MAIN')
    
    if is_reloader_process or is_first_time:
        if is_reloader_process:
            # Hanya tampilkan pada actual server process
            log_section(logger, "STARTING FLEXOTWIN BACKEND SERVER")
            logger.info("Server running at: http://0.0.0.0:5000")
            logger.info("API Documentation: http://0.0.0.0:5000/api/docs")
            logger.info("Health Check: http://0.0.0.0:5000/health")
            logger.info("Press CTRL+C to stop the server\n")
    
    app.run(
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=True
    )

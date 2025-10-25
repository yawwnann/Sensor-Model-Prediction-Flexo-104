"""
Routes Controller
Centralized route registration and management
"""

from flask import Flask
from src.controllers.health_controller import health_bp
from src.controllers.component_controller import component_bp
from src.controllers.prediction_controller import prediction_bp
from src.controllers.docs_controller import docs_bp
from src.controllers.downtime_controller import downtime_bp
from src.utils.logger import get_logger

logger = get_logger(__name__)


def register_routes(app: Flask) -> None:
    """
    Register semua blueprints/routes ke Flask app.
    
    Args:
        app: Flask application instance
    """
    try:
        # Register blueprints
        app.register_blueprint(health_bp, url_prefix='/api')
        app.register_blueprint(component_bp, url_prefix='/api')
        app.register_blueprint(prediction_bp, url_prefix='/api')
        app.register_blueprint(docs_bp, url_prefix='/api')
        app.register_blueprint(downtime_bp, url_prefix='/api')
        
        logger.info("All routes registered successfully")
        
        # Register error handlers
        register_error_handlers(app)
        
    except Exception as e:
        logger.error(f"Failed to register routes: {e}")
        raise


def register_error_handlers(app: Flask) -> None:
    """
    Register global error handlers.
    
    Args:
        app: Flask application instance
    """
    
    @app.errorhandler(404)
    def not_found(error):
        """Handler untuk endpoint yang tidak ditemukan."""
        logger.warning(f"404 Error: {error}")
        return {
            "error": "Endpoint tidak ditemukan",
            "message": "Silakan periksa URL yang Anda gunakan",
            "status_code": 404
        }, 404
    
    @app.errorhandler(500)
    def internal_error(error):
        """Handler untuk internal server error."""
        logger.error(f"500 Error: {error}")
        return {
            "error": "Internal Server Error",
            "message": "Terjadi kesalahan pada server",
            "status_code": 500
        }, 500
    
    @app.errorhandler(400)
    def bad_request(error):
        """Handler untuk bad request."""
        logger.warning(f"400 Error: {error}")
        return {
            "error": "Bad Request",
            "message": "Request tidak valid",
            "status_code": 400
        }, 400
    
    logger.info("Error handlers registered successfully")
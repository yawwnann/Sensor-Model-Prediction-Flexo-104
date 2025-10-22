"""
Prediction Controller
Endpoints untuk machine learning predictions
"""

from flask import Blueprint, jsonify, request
from src.services.prediction_service import PredictionService
from src.utils.logger import get_logger

# Setup
prediction_bp = Blueprint('predictions', __name__, url_prefix='/api')
logger = get_logger(__name__)
prediction_service = PredictionService()


@prediction_bp.route('/predict/maintenance', methods=['POST'])
def predict_single_maintenance():
    """
    Endpoint untuk prediksi durasi maintenance tunggal.
    
    Expected JSON body:
    {
        "total_produksi": 5000,
        "produk_cacat": 150
    }
    
    Returns:
        JSON response dengan hasil prediksi
    """
    logger.info("Single maintenance prediction requested")
    
    try:
        # Validasi dan ambil data JSON
        data = request.get_json()
        
        if not data:
            logger.warning("Empty request body")
            return jsonify({
                "error": "Request body kosong",
                "message": "Silakan kirim JSON data dengan struktur yang benar",
                "expected_format": {
                    "total_produksi": "number",
                    "produk_cacat": "number"
                },
                "example": {
                    "total_produksi": 5000,
                    "produk_cacat": 150
                }
            }), 400
        
        logger.info(f"Prediction request data: {data}")
        
        # Lakukan prediksi menggunakan service
        result = prediction_service.predict_maintenance_duration(data)
        
        # Return response berdasarkan hasil
        if result['success']:
            logger.info(f"Prediction successful: {result['prediction']} minutes")
            return jsonify(result), 200
        else:
            logger.warning(f"Prediction failed: {result['message']}")
            return jsonify(result), 400
            
    except Exception as e:
        logger.error(f"Error in single prediction: {e}")
        return jsonify({
            "error": "Error dalam prediksi",
            "message": str(e),
            "debug_info": {
                "endpoint": "/api/predict/maintenance",
                "method": "POST"
            }
        }), 500


@prediction_bp.route('/predict/maintenance/batch', methods=['POST'])
def predict_batch_maintenance():
    """
    Endpoint untuk prediksi durasi maintenance batch/multiple.
    
    Expected JSON body:
    {
        "data": [
            {"total_produksi": 5000, "produk_cacat": 150},
            {"total_produksi": 3000, "produk_cacat": 100}
        ]
    }
    
    Returns:
        JSON response dengan hasil prediksi batch
    """
    logger.info("Batch maintenance prediction requested")
    
    try:
        # Validasi dan ambil data JSON
        request_data = request.get_json()
        
        if not request_data or 'data' not in request_data:
            logger.warning("Invalid batch request format")
            return jsonify({
                "error": "Format request tidak valid",
                "message": "Silakan kirim JSON dengan key 'data' berisi list of objects",
                "expected_format": {
                    "data": [
                        {"total_produksi": "number", "produk_cacat": "number"}
                    ]
                },
                "example": {
                    "data": [
                        {"total_produksi": 5000, "produk_cacat": 150},
                        {"total_produksi": 3000, "produk_cacat": 100}
                    ]
                }
            }), 400
        
        data_list = request_data['data']
        
        if not isinstance(data_list, list):
            logger.warning("Data is not a list")
            return jsonify({
                "error": "Data harus berupa list",
                "message": "Key 'data' harus berisi list of objects"
            }), 400
        
        logger.info(f"Batch prediction request with {len(data_list)} items")
        
        # Lakukan batch prediksi menggunakan service
        result = prediction_service.batch_predict_maintenance_duration(data_list)
        
        logger.info(f"Batch prediction completed: {result['successful_predictions']}/{result['total_items']} successful")
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in batch prediction: {e}")
        return jsonify({
            "error": "Error dalam batch prediksi",
            "message": str(e),
            "debug_info": {
                "endpoint": "/api/predict/maintenance/batch",
                "method": "POST"
            }
        }), 500


@prediction_bp.route('/model/info', methods=['GET'])
def get_model_information():
    """
    Endpoint untuk mendapatkan informasi tentang model ML.
    
    Returns:
        JSON response dengan informasi model
    """
    logger.info("Model information requested")
    
    try:
        info = prediction_service.get_model_info()
        
        # Tambah informasi tambahan
        enhanced_info = {
            **info,
            "usage_examples": {
                "single_prediction": {
                    "url": "/api/predict/maintenance",
                    "method": "POST",
                    "body": {
                        "total_produksi": 5000,
                        "produk_cacat": 150
                    }
                },
                "batch_prediction": {
                    "url": "/api/predict/maintenance/batch",
                    "method": "POST",
                    "body": {
                        "data": [
                            {"total_produksi": 5000, "produk_cacat": 150},
                            {"total_produksi": 3000, "produk_cacat": 100}
                        ]
                    }
                }
            },
            "response_format": {
                "success": "boolean",
                "prediction": "float (minutes)",
                "prediction_formatted": "string (hours + minutes)",
                "input": "object (echoed input)",
                "message": "string (status message)"
            }
        }
        
        logger.info("Model information retrieved successfully")
        return jsonify(enhanced_info), 200
        
    except Exception as e:
        logger.error(f"Error getting model info: {e}")
        return jsonify({
            "error": "Error getting model info",
            "message": str(e)
        }), 500
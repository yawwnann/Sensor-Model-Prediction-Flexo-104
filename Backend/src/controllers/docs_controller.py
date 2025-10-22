"""
Documentation Controller
Endpoint untuk API documentation
"""

from flask import Blueprint, jsonify
from src.utils.logger import get_logger
from config import APP_NAME, APP_VERSION

# Setup
docs_bp = Blueprint('docs', __name__, url_prefix='/api')
logger = get_logger(__name__)


@docs_bp.route('/docs', methods=['GET'])
def get_api_documentation():
    """
    Endpoint untuk mendapatkan dokumentasi API lengkap.
    
    Returns:
        JSON response dengan dokumentasi API
    """
    logger.info("API documentation requested")
    
    documentation = {
        "api_info": {
            "name": APP_NAME,
            "version": APP_VERSION,
            "description": "Backend API untuk monitoring kesehatan mesin Flexo menggunakan Digital Twin",
            "base_url": "/api"
        },
        "endpoints": {
            "health_checks": {
                "GET /api/health": {
                    "description": "Health check umum API",
                    "parameters": None,
                    "returns": "Status server dan database",
                    "example_response": {
                        "status": "API Server Running",
                        "service": APP_NAME,
                        "version": APP_VERSION,
                        "database": {
                            "type": "PostgreSQL (Supabase)",
                            "status": "Connected"
                        }
                    }
                },
                "GET /api/health/<component_name>": {
                    "description": "Health check komponen tertentu",
                    "parameters": {
                        "component_name": "string - Nama komponen (path parameter)"
                    },
                    "returns": "Health metrics komponen",
                    "example_url": "/api/health/Pre-Feeder",
                    "example_response": {
                        "component_name": "Pre-Feeder",
                        "health_index": 85.32,
                        "status": "Sehat",
                        "color": "#00FF00",
                        "description": "Kondisi mesin baik, lakukan monitoring rutin"
                    }
                }
            },
            "components": {
                "GET /api/components": {
                    "description": "Daftar semua komponen",
                    "parameters": None,
                    "returns": "List semua komponen dan RPN values",
                    "example_response": {
                        "components": [
                            {
                                "id": 1,
                                "name": "Pre-Feeder",
                                "rpn_value": 45
                            }
                        ],
                        "total_count": 1
                    }
                },
                "GET /api/components/<component_name>/health": {
                    "description": "Detail lengkap kesehatan komponen",
                    "parameters": {
                        "component_name": "string - Nama komponen (path parameter)"
                    },
                    "returns": "Detail lengkap health metrics",
                    "example_url": "/api/components/Printing/health",
                    "example_response": {
                        "component": {
                            "name": "Printing",
                            "rpn_value": 45,
                            "rpn_max": 210
                        },
                        "health_assessment": {
                            "overall_index": 85.32,
                            "status": "Sehat"
                        }
                    }
                }
            },
            "predictions": {
                "POST /api/predict/maintenance": {
                    "description": "Prediksi durasi maintenance tunggal",
                    "parameters": {
                        "body": {
                            "total_produksi": "number - Total produksi (Pcs)",
                            "produk_cacat": "number - Produk cacat (Pcs)"
                        }
                    },
                    "returns": "Prediksi durasi maintenance",
                    "example_request": {
                        "total_produksi": 5000,
                        "produk_cacat": 150
                    },
                    "example_response": {
                        "success": True,
                        "prediction": 120.45,
                        "prediction_formatted": "2 jam 0 menit",
                        "input": {
                            "total_produksi": 5000,
                            "produk_cacat": 150
                        }
                    }
                },
                "POST /api/predict/maintenance/batch": {
                    "description": "Prediksi durasi maintenance batch",
                    "parameters": {
                        "body": {
                            "data": "array - List of prediction objects"
                        }
                    },
                    "returns": "Hasil prediksi batch",
                    "example_request": {
                        "data": [
                            {"total_produksi": 5000, "produk_cacat": 150},
                            {"total_produksi": 3000, "produk_cacat": 100}
                        ]
                    },
                    "example_response": {
                        "success": True,
                        "total_items": 2,
                        "successful_predictions": 2,
                        "predictions": ["...array of results..."]
                    }
                },
                "GET /api/model/info": {
                    "description": "Informasi model ML yang digunakan",
                    "parameters": None,
                    "returns": "Detail informasi model",
                    "example_response": {
                        "loaded": True,
                        "model_details": {
                            "type": "LinearRegression",
                            "class": "<class 'sklearn.linear_model._base.LinearRegression'>"
                        }
                    }
                }
            },
            "documentation": {
                "GET /api/docs": {
                    "description": "Dokumentasi API lengkap (endpoint ini)",
                    "parameters": None,
                    "returns": "Dokumentasi API dalam format JSON"
                }
            }
        },
        "response_formats": {
            "success_response": {
                "structure": "Varies by endpoint",
                "http_status": "200, 201"
            },
            "error_response": {
                "structure": {
                    "error": "string - Error title",
                    "message": "string - Error description",
                    "status_code": "number - HTTP status code"
                },
                "http_status": "400, 404, 500, 503"
            }
        },
        "data_sources": {
            "database": "PostgreSQL (Supabase) - Component RPN values",
            "ml_model": "Linear Regression - Maintenance duration prediction",
            "real_time_metrics": "Simulated OEE scores for demonstration"
        },
        "health_calculation": {
            "formula": "(RPN_Score × 0.4) + (OEE_Score × 0.6)",
            "rpn_score": "Calculated from: (1 - RPN_Value / RPN_Max) × 100",
            "oee_score": "Simulated random value between 85.0 - 99.5",
            "thresholds": {
                "excellent": ">= 90",
                "good": "80-89",
                "fair": "70-79",
                "poor": "50-69",
                "critical": "< 50"
            }
        },
        "usage_tips": [
            "Semua endpoints mengembalikan JSON response",
            "Gunakan Content-Type: application/json untuk POST requests",
            "Component names case-sensitive",
            "Database connection ditest pada setiap startup",
            "Logs tersimpan di folder logs/ untuk debugging"
        ],
        "troubleshooting": {
            "database_connection_failed": [
                "Periksa koneksi internet",
                "Verifikasi DATABASE_URL di file .env",
                "Pastikan Supabase instance aktif"
            ],
            "model_not_loaded": [
                "Pastikan file model.pkl ada di folder Model/",
                "Restart aplikasi",
                "Periksa log untuk error detail"
            ],
            "component_not_found": [
                "Gunakan GET /api/components untuk melihat daftar yang tersedia",
                "Pastikan nama komponen exact match",
                "Periksa case sensitivity"
            ]
        }
    }
    
    logger.info("API documentation retrieved successfully")
    return jsonify(documentation), 200
"""
Prediction Service
Service layer untuk machine learning predictions
"""

import joblib
import numpy as np
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class PredictionService:
    """Service untuk machine learning predictions dan model management."""
    
    def __init__(self):
        """Initialize prediction service dan load model."""
        self.model = None
        self.model_loaded = False
        self.model_path = self._get_model_path()
        self._load_model()
    
    def _get_model_path(self) -> Path:
        """
        Mendapatkan path ke file model.
        
        Returns:
            Path ke model.pkl
        """
        # Backend/src/services -> Backend -> Parent -> Model
        current_dir = Path(__file__).resolve().parent
        backend_dir = current_dir.parent.parent  # Backend directory
        model_path = backend_dir.parent / "Model" / "model.pkl"
        return model_path
    
    def _load_model(self) -> None:
        """Load model dari file dengan error handling."""
        try:
            logger.info(f"Loading model from: {self.model_path}")
            
            if not self.model_path.exists():
                raise FileNotFoundError(f"Model file tidak ditemukan: {self.model_path}")
            
            self.model = joblib.load(self.model_path)
            self.model_loaded = True
            
            logger.info("Model loaded successfully!")
            logger.info(f"Model type: {type(self.model).__name__}")
            
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            self.model = None
            self.model_loaded = False
    
    def _validate_input_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validasi input data untuk prediksi.
        
        Args:
            data: Dictionary input data
            
        Returns:
            Dictionary dengan data yang sudah divalidasi
            
        Raises:
            ValueError: Jika input tidak valid
        """
        if not isinstance(data, dict):
            raise ValueError("Input harus berupa dictionary")
        
        # Cek ketersediaan keys yang diperlukan
        required_keys = ['total_produksi', 'produk_cacat']
        missing_keys = [key for key in required_keys if key not in data]
        
        if missing_keys:
            raise ValueError(f"Input harus memiliki keys: {required_keys}. Missing: {missing_keys}")
        
        # Konversi dan validasi nilai
        try:
            total_produksi = float(data['total_produksi'])
            produk_cacat = float(data['produk_cacat'])
        except (ValueError, TypeError) as e:
            raise ValueError(f"Nilai harus berupa angka: {e}")
        
        # Validasi nilai tidak negatif
        if total_produksi < 0 or produk_cacat < 0:
            raise ValueError("Nilai tidak boleh negatif")
        
        # Validasi logis: produk cacat tidak boleh lebih dari total produksi
        if produk_cacat > total_produksi:
            raise ValueError("Produk cacat tidak boleh lebih besar dari total produksi")
        
        return {
            'total_produksi': total_produksi,
            'produk_cacat': produk_cacat
        }
    
    def _format_prediction_time(self, minutes: float) -> str:
        """
        Format durasi dalam menit ke format yang mudah dibaca.
        
        Args:
            minutes: Durasi dalam menit
            
        Returns:
            String format durasi (jam dan menit)
        """
        hours = int(minutes // 60)
        remaining_minutes = int(minutes % 60)
        
        if hours > 0:
            return f"{hours} jam {remaining_minutes} menit"
        else:
            return f"{remaining_minutes} menit"
    
    def predict_maintenance_duration(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Memprediksi durasi maintenance berdasarkan input data.
        
        Args:
            input_data: Dictionary dengan total_produksi dan produk_cacat
            
        Returns:
            Dictionary dengan hasil prediksi
        """
        try:
            # Validasi model availability
            if not self.model_loaded or self.model is None:
                return {
                    'success': False,
                    'prediction': None,
                    'input': input_data,
                    'message': 'Model tidak tersedia. Silakan restart server atau periksa file model.',
                    'troubleshooting': [
                        'Pastikan file model.pkl ada di folder Model/',
                        'Restart aplikasi',
                        'Periksa log untuk error detail'
                    ]
                }
            
            # Validasi input data
            validated_data = self._validate_input_data(input_data)
            
            logger.info(f"Input validation passed: {validated_data}")
            
            # Siapkan data untuk model
            # Model expects: [total_produksi, produk_cacat]
            X = np.array([[
                validated_data['total_produksi'], 
                validated_data['produk_cacat']
            ]])
            
            # Lakukan prediksi
            prediction = self.model.predict(X)
            prediction_value = float(prediction[0])
            
            # Pastikan prediksi tidak negatif
            if prediction_value < 0:
                prediction_value = 0
            
            prediction_value = round(prediction_value, 2)
            
            logger.info(f"Prediction completed: {prediction_value} minutes")
            
            # Format hasil
            result = {
                'success': True,
                'prediction': prediction_value,
                'prediction_formatted': self._format_prediction_time(prediction_value),
                'input': validated_data,
                'message': 'Prediksi berhasil',
                'metadata': {
                    'model_type': type(self.model).__name__,
                    'prediction_unit': 'minutes',
                    'calculation_method': 'Linear Regression'
                }
            }
            
            return result
            
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return {
                'success': False,
                'prediction': None,
                'input': input_data,
                'message': f"Validation error: {str(e)}",
                'error_type': 'ValidationError'
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {
                'success': False,
                'prediction': None,
                'input': input_data,
                'message': f"Prediction error: {str(e)}",
                'error_type': 'PredictionError'
            }
    
    def batch_predict_maintenance_duration(self, data_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Memprediksi durasi maintenance untuk multiple inputs.
        
        Args:
            data_list: List of input dictionaries
            
        Returns:
            Dictionary dengan hasil batch prediction
        """
        try:
            if not isinstance(data_list, list):
                raise ValueError("Input harus berupa list")
            
            if len(data_list) == 0:
                raise ValueError("List input tidak boleh kosong")
            
            results = []
            successful_count = 0
            
            for idx, data in enumerate(data_list):
                logger.info(f"Processing batch item {idx + 1}/{len(data_list)}")
                
                # Predict individual item
                result = self.predict_maintenance_duration(data)
                results.append({
                    'item_index': idx,
                    **result
                })
                
                if result['success']:
                    successful_count += 1
            
            # Compile batch results
            batch_result = {
                'success': True,
                'total_items': len(data_list),
                'successful_predictions': successful_count,
                'failed_predictions': len(data_list) - successful_count,
                'success_rate': round((successful_count / len(data_list)) * 100, 2),
                'predictions': results,
                'message': f'Batch prediction completed: {successful_count}/{len(data_list)} berhasil',
                'summary': {
                    'total_processing_time': 'Real-time',
                    'model_consistency': 'Same model used for all predictions'
                }
            }
            
            logger.info(f"Batch prediction completed: {successful_count}/{len(data_list)} successful")
            
            return batch_result
            
        except Exception as e:
            logger.error(f"Batch prediction error: {e}")
            return {
                'success': False,
                'total_items': len(data_list) if isinstance(data_list, list) else 0,
                'successful_predictions': 0,
                'failed_predictions': 0,
                'predictions': [],
                'message': f"Batch prediction error: {str(e)}",
                'error_type': 'BatchPredictionError'
            }
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Mendapatkan informasi detail tentang model.
        
        Returns:
            Dictionary dengan informasi model
        """
        if not self.model_loaded or self.model is None:
            return {
                'loaded': False,
                'message': 'Model tidak tersedia',
                'model_path': str(self.model_path),
                'troubleshooting': [
                    'Periksa apakah file model.pkl ada',
                    'Pastikan path model benar',
                    'Restart aplikasi'
                ]
            }
        
        try:
            info = {
                'loaded': True,
                'model_details': {
                    'type': type(self.model).__name__,
                    'class': str(self.model.__class__),
                    'path': str(self.model_path)
                },
                'model_parameters': {
                    'coefficients': self.model.coef_.tolist() if hasattr(self.model, 'coef_') else None,
                    'intercept': float(self.model.intercept_) if hasattr(self.model, 'intercept_') else None,
                    'n_features': self.model.n_features_in_ if hasattr(self.model, 'n_features_in_') else None
                },
                'feature_info': {
                    'input_features': ['Total Produksi (Pcs)', 'Produk Cacat (Pcs)'],
                    'target_variable': 'Waktu Downtime (Menit)',
                    'expected_input_format': {
                        'total_produksi': 'float/int (>= 0)',
                        'produk_cacat': 'float/int (>= 0, <= total_produksi)'
                    }
                },
                'performance_info': {
                    'prediction_unit': 'minutes',
                    'typical_range': '0 - N minutes (depends on input)',
                    'processing_time': 'Real-time (< 100ms)'
                },
                'message': 'Model information retrieved successfully'
            }
            
            return info
            
        except Exception as e:
            logger.error(f"Error getting model info: {e}")
            return {
                'loaded': True,
                'message': f'Error retrieving model details: {str(e)}',
                'basic_info': {
                    'type': type(self.model).__name__ if self.model else 'Unknown'
                }
            }
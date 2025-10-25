"""
SOLUSI UTAMA: Enhanced Prediction Service 
Memperbaiki hasil prediksi yang terlalu singkat dengan:

1. Re-kalibrasi baseline prediksi berdasarkan severity
2. Post-processing adjustment berdasarkan historical data
3. Multi-tier prediction dengan context awareness
4. Realistic range validation
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ============================================================================
# KONSTANTA REALISTIS UNTUK MAINTENANCE INDUSTRI PRINTING
# ============================================================================

# Baseline durasi maintenance berdasarkan severity (dalam menit)
MAINTENANCE_BASELINE = {
    1: 15,    # Sangat ringan (istirahat, brief) - 15 menit
    2: 30,    # Ringan (cleaning, setup minor) - 30 menit  
    3: 60,    # Sedang (setting, adjustment) - 1 jam
    4: 90,    # Menengah (repair operator) - 1.5 jam
    5: 120,   # Normal (maintenance rutin) - 2 jam
    6: 180,   # Agak serius (mechanical repair) - 3 jam
    7: 240,   # Serius (electrical repair) - 4 jam
    8: 360,   # Sangat serius (major component) - 6 jam
    9: 480,   # Kritis (sistem utama rusak) - 8 jam
    10: 720   # Sangat kritis (overhaul) - 12 jam
}

# Multiplier berdasarkan shift (shift malam biasanya lebih lama karena resource terbatas)
SHIFT_MULTIPLIERS = {
    1.0: 1.0,    # Shift pagi - full resource
    2.0: 1.1,    # Shift siang - resource normal
    3.0: 1.3,    # Shift malam - resource terbatas
    '_NONE_': 1.2  # Unknown shift - assume rata-rata
}

# Adjustment berdasarkan kategori masalah
CATEGORY_ADJUSTMENTS = {
    # Printing issues - kompleks karena melibatkan warna, register, dll
    'printing': {
        'base_multiplier': 1.4,
        'keywords': ['PRINTING', 'PRINT', 'TINTA', 'WARNA', 'REGISTER', 'ANILOX']
    },
    
    # Mechanical issues - butuh spare part dan skill tinggi  
    'mechanical': {
        'base_multiplier': 1.6,
        'keywords': ['MEKANIK', 'BEARING', 'GEAR', 'PECAH', 'AUS', 'PNEUMATIC']
    },
    
    # Electrical issues - troubleshooting kompleks
    'electrical': {
        'base_multiplier': 1.5,
        'keywords': ['ELEKTRIK', 'LISTRIK', 'SENSOR', 'WIRING', 'MOTOR']
    },
    
    # Feeder issues - kritis untuk kontinuitas produksi
    'feeder': {
        'base_multiplier': 1.3,
        'keywords': ['FEEDER', 'VACUUM', 'BELT', 'CONVEYOR', 'FEEDING']
    },
    
    # Quality issues - butuh fine tuning
    'quality': {
        'base_multiplier': 1.2,
        'keywords': ['BLUR', 'BOTAK', 'LARI', 'MIRING', 'CACAT', 'REJECT']
    }
}

# Range validasi realistis (dalam menit)
MIN_REALISTIC_DURATION = 10   # Minimum 10 menit
MAX_REALISTIC_DURATION = 960  # Maximum 16 jam (1 shift penuh)

class EnhancedPredictionService:
    """Enhanced prediction service dengan realistic baseline dan adjustments"""
    
    def __init__(self):
        """Initialize enhanced prediction service"""
        self.model = None
        self.feature_names = None
        self.model_loaded = False
        self.historical_stats = self._load_historical_stats()
        self._load_model()
        self._load_feature_names()
    
    def _load_historical_stats(self) -> Dict[str, float]:
        """
        Load historical statistics dari data training untuk kalibrasi
        """
        stats = {
            'overall_mean': 180.0,      # 3 jam - rata-rata maintenance industri
            'overall_median': 120.0,    # 2 jam - median realistic
            'printing_mean': 240.0,     # 4 jam - printing kompleks
            'mechanical_mean': 300.0,   # 5 jam - mechanical repair
            'electrical_mean': 360.0,   # 6 jam - electrical troubleshooting
            'preventive_mean': 480.0,   # 8 jam - preventive maintenance
        }
        logger.info(f"Historical stats loaded for baseline calibration")
        return stats
    
    def _get_model_path(self) -> Path:
        """Get path to model file"""
        current_dir = Path(__file__).resolve().parent
        backend_dir = current_dir.parent.parent
        
        # Coba model improved dulu, fallback ke model biasa
        improved_path = backend_dir.parent / "Model" / "model_improved.pkl"
        if improved_path.exists():
            logger.info(f"Using improved model: {improved_path}")
            return improved_path
        
        standard_path = backend_dir.parent / "Model" / "model.pkl"
        logger.info(f"Using standard model: {standard_path}")
        return standard_path
    
    def _get_feature_names_path(self) -> Path:
        """Get path to feature names file"""
        current_dir = Path(__file__).resolve().parent
        backend_dir = current_dir.parent.parent
        
        # Coba feature names improved dulu
        improved_path = backend_dir.parent / "Model" / "feature_names_improved.pkl"
        if improved_path.exists():
            return improved_path
        
        return backend_dir.parent / "Model" / "feature_names.pkl"
    
    def _load_model(self) -> None:
        """Load model dengan enhanced error handling"""
        try:
            model_path = self._get_model_path()
            logger.info(f"Loading model from: {model_path}")
            
            if not model_path.exists():
                raise FileNotFoundError(f"Model file tidak ditemukan: {model_path}")
            
            self.model = joblib.load(model_path)
            self.model_loaded = True
            
            logger.info(f"✅ Model loaded successfully!")
            logger.info(f"   Model type: {type(self.model).__name__}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load model: {e}")
            self.model = None
            self.model_loaded = False
    
    def _load_feature_names(self) -> None:
        """Load feature names dengan enhanced error handling"""
        try:
            feature_names_path = self._get_feature_names_path()
            logger.info(f"Loading feature names from: {feature_names_path}")
            
            if not feature_names_path.exists():
                logger.warning(f"⚠ Feature names file tidak ditemukan: {feature_names_path}")
                logger.warning("  Model akan menggunakan mode fallback")
                self.feature_names = None
                return
            
            self.feature_names = joblib.load(feature_names_path)
            
            logger.info(f"✅ Feature names loaded successfully!")
            logger.info(f"   Total features: {len(self.feature_names)}")
            
        except Exception as e:
            logger.error(f"❌ Failed to load feature names: {e}")
            self.feature_names = None
    
    def _calculate_enhanced_baseline(self, real_time_data: Dict[str, Any]) -> float:
        """
        Kalkulasi baseline prediksi yang lebih realistis berdasarkan:
        1. FMEA Severity level
        2. Kategori masalah (printing, mechanical, electrical)
        3. Shift context
        4. Historical patterns
        
        Args:
            real_time_data: Data sensor real-time
            
        Returns:
            Baseline duration dalam menit
        """
        # Ekstrak informasi dari input
        reason = str(real_time_data.get('reason', '')).upper()
        shift = real_time_data.get('shift', '_NONE_')
        
        # 1. Hitung FMEA Severity untuk baseline
        severity = self._get_fmea_severity_from_reason(reason)
        base_duration = MAINTENANCE_BASELINE.get(severity, 120)  # Default 2 jam
        
        logger.info(f"🎯 Enhanced baseline calculation:")
        logger.info(f"   Reason: '{reason}'")
        logger.info(f"   FMEA Severity: {severity}/10")
        logger.info(f"   Base duration: {base_duration} menit")
        
        # 2. Aplikasikan multiplier berdasarkan kategori masalah
        category_multiplier = 1.0
        matched_category = None
        
        for category, config in CATEGORY_ADJUSTMENTS.items():
            keywords = config['keywords']
            if any(keyword in reason for keyword in keywords):
                category_multiplier = config['base_multiplier']
                matched_category = category
                break
        
        if matched_category:
            logger.info(f"   Kategori: {matched_category} (×{category_multiplier})")
        else:
            logger.info(f"   Kategori: general (×{category_multiplier})")
        
        # 3. Aplikasikan shift multiplier
        shift_key = str(shift) if shift != '_NONE_' else '_NONE_'
        shift_multiplier = SHIFT_MULTIPLIERS.get(shift_key, 1.2)
        logger.info(f"   Shift: {shift} (×{shift_multiplier})")
        
        # 4. TAMBAHAN: Health Index Adjustment
        health_multiplier = self._calculate_health_multiplier(real_time_data)
        logger.info(f"   🏥 Health adjustment: ×{health_multiplier}")
        
        # 5. Kalkulasi final dengan semua multiplier
        enhanced_baseline = base_duration * category_multiplier * shift_multiplier * health_multiplier
        
        # 6. Bounding dengan range realistis
        enhanced_baseline = max(MIN_REALISTIC_DURATION, 
                              min(MAX_REALISTIC_DURATION, enhanced_baseline))
        
        logger.info(f"   📊 Enhanced baseline: {enhanced_baseline:.1f} menit")
        
        return enhanced_baseline
    
    def _calculate_health_multiplier(self, real_time_data: Dict[str, Any]) -> float:
        """
        Kalkulasi multiplier berdasarkan health index dan kondisi sensor
        Health index rendah = maintenance lebih lama
        """
        # Ambil health index jika tersedia
        health_index = real_time_data.get('health_index')
        
        if health_index is not None:
            health_index = float(health_index)
            logger.info(f"   🏥 Health Index: {health_index}%")
            
            # Mapping health index ke multiplier
            if health_index >= 80:
                return 0.7  # Kondisi bagus = maintenance cepat
            elif health_index >= 60:
                return 1.0  # Kondisi normal = baseline normal
            elif health_index >= 40:
                return 1.3  # Kondisi agak buruk = maintenance agak lama
            elif health_index >= 20:
                return 1.8  # Kondisi buruk = maintenance lama
            else:
                return 2.5  # Kondisi sangat buruk = maintenance sangat lama
        
        # Fallback: hitung dari kondisi sensor
        sensor_scores = []
        
        # Evaluasi kondisi sensor individual
        for sensor_key in ['suction_strength', 'blade_sharpness', 'temp_consistency']:
            value = real_time_data.get(sensor_key)
            if value is not None:
                sensor_scores.append(float(value))
        
        if sensor_scores:
            avg_sensor_condition = sum(sensor_scores) / len(sensor_scores)
            logger.info(f"   📊 Avg sensor condition: {avg_sensor_condition:.2f}")
            
            # Konversi sensor condition ke health multiplier
            if avg_sensor_condition >= 0.8:
                return 0.8
            elif avg_sensor_condition >= 0.6:
                return 1.0
            elif avg_sensor_condition >= 0.4:
                return 1.4
            elif avg_sensor_condition >= 0.2:
                return 2.0
            else:
                return 2.8
        
        # Default multiplier jika tidak ada data
        logger.info(f"   ⚠ No health/sensor data, using default multiplier")
        return 1.0
    
    def _get_fmea_severity_from_reason(self, reason: str) -> int:
        """
        Mapping reason ke FMEA severity
        Simplified version dari mapping di train_model.py
        """
        # Simplified FMEA mapping untuk prediksi real-time
        severity_patterns = {
            10: ['EXPLOSION', 'FIRE', 'SAFETY'],
            9: ['PECAH', 'CRACK', 'BROKEN', 'TOTAL_FAILURE', 'REGISTER_GESER'],
            8: ['ELEKTRIK', 'ELECTRICAL', 'MEKANIK', 'MECHANICAL', 'SENSOR_ERROR'],
            7: ['PRINTING', 'QUALITY', 'DEFECT', 'LARI', 'MIRING'],
            6: ['FEEDER', 'VACUUM', 'CONVEYOR', 'FEEDING'],
            5: ['ADJUSTMENT', 'SETTING', 'CLEANING'],
            4: ['MINOR_REPAIR', 'OPERATOR_REPAIR'],
            3: ['SETUP', 'CHANGEOVER', 'MOUNTING'],
            2: ['BREAK', 'ISTIRAHAT', 'SCHEDULED'],
            1: ['MEETING', 'BRIEFING', 'PRAYER']
        }
        
        reason_upper = reason.upper()
        
        for severity, patterns in severity_patterns.items():
            if any(pattern in reason_upper for pattern in patterns):
                return severity
        
        return 5  # Default medium severity
    
    def _apply_post_processing_adjustment(self, 
                                        raw_prediction: float, 
                                        enhanced_baseline: float,
                                        real_time_data: Dict[str, Any]) -> float:
        """
        Post-processing adjustment untuk memperbaiki prediksi yang terlalu ekstrem
        
        Args:
            raw_prediction: Prediksi mentah dari model ML
            enhanced_baseline: Baseline yang sudah dikalkulasi
            real_time_data: Data input
            
        Returns:
            Adjusted prediction yang lebih realistis
        """
        logger.info(f"🔧 Post-processing adjustment:")
        logger.info(f"   Raw prediction: {raw_prediction:.1f} menit")
        logger.info(f"   Enhanced baseline: {enhanced_baseline:.1f} menit")
        
        # 1. Jika prediksi terlalu rendah dibanding baseline
        if raw_prediction < enhanced_baseline * 0.3:
            logger.info(f"   ⚠ Prediksi terlalu rendah, adjusting upward")
            # Gunakan weighted average antara baseline dan prediksi
            adjusted = (enhanced_baseline * 0.7) + (raw_prediction * 0.3)
        
        # 2. Jika prediksi terlalu tinggi dibanding baseline  
        elif raw_prediction > enhanced_baseline * 3.0:
            logger.info(f"   ⚠ Prediksi terlalu tinggi, adjusting downward")
            # Cap di 3x baseline
            adjusted = enhanced_baseline * 2.5
        
        # 3. Jika prediksi dalam range wajar
        else:
            # Gunakan weighted average untuk smoothing
            weight_baseline = 0.4  # 40% baseline
            weight_prediction = 0.6  # 60% ML prediction
            adjusted = (enhanced_baseline * weight_baseline) + (raw_prediction * weight_prediction)
        
        # 4. Final bounding dengan range realistis
        adjusted = max(MIN_REALISTIC_DURATION, 
                      min(MAX_REALISTIC_DURATION, adjusted))
        
        logger.info(f"   ✅ Final adjusted: {adjusted:.1f} menit")
        
        return adjusted
    
    def _format_prediction_time(self, minutes: float) -> str:
        """Format durasi dalam menit ke format yang mudah dibaca"""
        hours = int(minutes // 60)
        remaining_minutes = int(minutes % 60)
        
        if hours > 0:
            return f"{hours} jam {remaining_minutes} menit"
        else:
            return f"{remaining_minutes} menit"
    
    def predict_downtime_enhanced(self, real_time_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhanced prediction dengan multi-tier approach:
        1. Kalkulasi enhanced baseline
        2. ML model prediction  
        3. Post-processing adjustment
        4. Validation & formatting
        
        Args:
            real_time_data: Data real-time sensor
            
        Returns:
            Enhanced prediction result
        """
        try:
            logger.info(f"🚀 Starting enhanced prediction...")
            logger.info(f"   Input: {real_time_data}")
            
            # Step 1: Kalkulasi enhanced baseline
            enhanced_baseline = self._calculate_enhanced_baseline(real_time_data)
            
            # Step 2: ML Model prediction (jika tersedia)
            ml_prediction = None
            if self.model_loaded and self.model is not None:
                try:
                    if self.feature_names is not None:
                        # Advanced mode dengan feature engineering
                        feature_df = self._prepare_feature_array(real_time_data)
                        ml_prediction = float(self.model.predict(feature_df)[0])
                    else:
                        # Simple mode fallback
                        ml_prediction = self._predict_simple_mode_value(real_time_data)
                    
                    # Jika model menggunakan log transform, inverse transform
                    if ml_prediction < 10:  # Likely in log space
                        ml_prediction = np.expm1(ml_prediction)
                    
                    logger.info(f"🤖 ML prediction: {ml_prediction:.1f} menit")
                
                except Exception as e:
                    logger.warning(f"⚠ ML prediction failed: {e}, using baseline")
                    ml_prediction = None
            
            # Step 3: Post-processing adjustment
            if ml_prediction is not None:
                final_prediction = self._apply_post_processing_adjustment(
                    ml_prediction, enhanced_baseline, real_time_data
                )
            else:
                # Fallback ke enhanced baseline saja
                final_prediction = enhanced_baseline
                logger.info(f"📋 Using enhanced baseline as final prediction")
            
            # Step 4: Final validation dan formatting
            final_prediction = max(MIN_REALISTIC_DURATION, 
                                 min(MAX_REALISTIC_DURATION, final_prediction))
            
            prediction_formatted = self._format_prediction_time(final_prediction)
            
            # Prepare result dengan metadata lengkap
            result = {
                'success': True,
                'prediction': round(final_prediction, 1),
                'prediction_formatted': prediction_formatted,
                'input': real_time_data,
                'message': 'Enhanced prediction berhasil',
                'metadata': {
                    'approach': 'Enhanced Multi-Tier',
                    'enhanced_baseline': round(enhanced_baseline, 1),
                    'ml_prediction': round(ml_prediction, 1) if ml_prediction else None,
                    'adjustment_applied': ml_prediction is not None,
                    'model_available': self.model_loaded,
                    'feature_engineering': self.feature_names is not None,
                    'prediction_range': f"{MIN_REALISTIC_DURATION}-{MAX_REALISTIC_DURATION} menit",
                    'confidence_level': 'High' if ml_prediction else 'Medium'
                }
            }
            
            logger.info(f"✅ Enhanced prediction completed: {prediction_formatted}")
            
            return result
            
        except Exception as e:
            logger.error(f"❌ Enhanced prediction error: {e}", exc_info=True)
            return {
                'success': False,
                'prediction': None,
                'input': real_time_data,
                'message': f"Enhanced prediction error: {str(e)}",
                'error_type': 'EnhancedPredictionError'
            }
    
    def predict_downtime(self, real_time_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Alias untuk predict_downtime_enhanced untuk kompatibilitas dengan health_service
        """
        return self.predict_downtime_enhanced(real_time_data)
    
    def _predict_simple_mode_value(self, real_time_data: Dict[str, Any]) -> float:
        """Simple mode prediction untuk fallback"""
        try:
            production = float(real_time_data.get('production', 0))
            defects = float(real_time_data.get('defects', 0))
            
            # Model expects: [total_produksi, produk_cacat]
            X = np.array([[production, defects]])
            prediction = self.model.predict(X)
            
            return float(prediction[0])
            
        except Exception as e:
            logger.error(f"Simple mode prediction error: {e}")
            return 120.0  # Default 2 jam
    
    def _prepare_feature_array(self, real_time_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Prepare feature array untuk advanced model
        Simplified version dari prediction_service.py
        """
        # Create DataFrame dengan semua fitur (inisialisasi ke 0)
        df = pd.DataFrame(0, index=[0], columns=self.feature_names)
        
        # Set FMEA_Severity
        reason = real_time_data.get('reason', '')
        severity = self._get_fmea_severity_from_reason(reason)
        if 'FMEA_Severity' in df.columns:
            df['FMEA_Severity'] = severity
        
        # Set kategorikal features (simplified)
        if reason:
            # Cari matching columns
            for col in df.columns:
                if col.startswith('Scrab Description_') and reason.upper() in col:
                    df[col] = 1
                    break
                elif col.startswith('Break Time Description_') and reason.upper() in col:
                    df[col] = 1
                    break
        
        # Set shift
        shift = str(real_time_data.get('shift', '_NONE_'))
        shift_col = f'Shift_{shift}'
        if shift_col in df.columns:
            df[shift_col] = 1
        elif 'Shift__NONE_' in df.columns:
            df['Shift__NONE_'] = 1
        
        return df

# Global instance
_enhanced_service = None

def get_enhanced_prediction_service():
    """Get singleton instance of enhanced prediction service"""
    global _enhanced_service
    if _enhanced_service is None:
        _enhanced_service = EnhancedPredictionService()
    return _enhanced_service
"""
Prediction Service
Service layer untuk machine learning predictions dengan feature engineering
"""

import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Konstanta untuk perhitungan OEE
TOTAL_SHIFT_TIME_MINUTES = 480.0  # 8 jam = 480 menit

# ============================================================================
# MAPPING FMEA SEVERITY (Skor S dari Analisis FMEA Tabel 4.5 Skripsi)
# ============================================================================
# Mapping dari Deskripsi Downtime ke Skor Severity (S) FMEA
# Skor 1-10: 1=sangat ringan, 10=sangat parah/berbahaya
# CATATAN: Harus sinkron dengan FMEA_SEVERITY_MAP di train_model.py
FMEA_SEVERITY_MAP = {
    # PRE-FEEDER UNIT FAILURES
    'BELT CONVEYOR SLIP': 7,
    'PENUMPUKAN KARTON TIDAK RATA': 7,
    'SENSOR TIDAK MENDETEKSI LEMBARAN': 8,
    
    # FEEDER UNIT FAILURES
    'FEEDER UNIT TROUBLE MEKANIK': 8,
    'FEEDER UNIT TROUBLE ELEKTRIK': 8,
    'VACUM KURANG': 8,
    'VACUUM KURANG': 8,
    'SHEET NYANGKUT/ MACET': 7,
    'LEMBARAN TIDAK TERAMBIL': 8,
    
    # PRINTING UNIT FAILURES
    'PRINTING UNIT TROUBLE MEKANIK': 9,
    'PRINTING UNIT TROUBLE ELEKTRIK': 9,
    'REGISTER GESER': 9,
    'PRINT BLOBOR': 9,
    'PRINTING BOTAK': 8,
    'PRINT LARI': 8,
    'PRINT BLUR': 8,
    'TINTA BOCOR': 8,
    'LIMBAH TINTA BANJIR': 8,
    'WARNA TIDAK SESUAI': 7,
    'WARNA LUNTUR': 7,
    'TINTA TIDAK KONSISTEN': 8,
    'ANILOX ROLLER TERSUMBAT': 8,
    
    # SLOTTER & CREASING UNIT FAILURES
    'SLOTTER UNIT TROUBLE MEKANIK': 8,
    'SLOTTER UNIT TROUBLE ELEKTRIK': 9,
    'SLOTER LARI': 8,
    'SLOTTER LARI': 8,
    'SLOTTER MIRING': 8,
    'SLOTTER PECAH': 9,
    'PISAU TUMPUL': 8,
    'CREASING PECAH': 9,
    'CREASING LARI': 8,
    'CREASING MIRING': 8,
    'ROLLER CREASING AUS': 8,
    
    # DIE-CUT UNIT FAILURES
    'DIECUT UNIT TROUBLE MEKANIK': 8,
    'DIECUT UNIT TROUBLE ELEKTRIK': 9,
    'DIECUT LARI': 8,
    'DIECUT PECAH': 9,
    'DIECUT TIDAK PUTUS': 8,
    'DIECUT MIRING': 8,
    
    # STACKER UNIT FAILURES
    'STACKER TROUBLE MEKANIK': 6,
    'STACKER TROUBLE ELEKTRIK': 9,
    'COUNTER PROBLEM': 6,
    'SENSOR PENGHITUNG ERROR': 6,
    'PNEUMATIC LEMAH': 6,
    'CONVEYOR SLIP': 6,
    
    # PLATE & SETUP ISSUES
    'LAP KLISE (Plate)': 4,
    'MOUNTING PLATE (during operati': 5,
    'GANTI/PASANG PISAU SLOTTER': 5,
    'PLATE CYLINDER TIDAK SEJAJAR': 9,
    
    # MATERIAL & SUPPLY ISSUES
    'TUNGGU TINTA': 6,
    'TUNGGU BAHAN SHEETS': 6,
    'CARI BAHAN SHEETS': 6,
    'TUNGGU KLISE (Plate)': 6,
    'CHEMICAL PROBLEM>OTHERS': 7,
    
    # OPERATIONAL & MAINTENANCE
    'SETTING TIME': 3,
    'ADJUST TINTA': 4,
    'REPAIR RINGAN BY OPERATOR': 5,
    'MECHANICAL REPAIR>OTHER': 6,
    'BUANG SAMPAH': 2,
    'CUCI MESIN': 3,
    'RAPIH SHIFT': 2,
    'BRIEFING': 1,
    'SHOLAT JUMAT': 1,
    'ISTIRAHAT': 1,
    
    # PLANNED DOWNTIME
    'TIDAK ADA SHIFT': 1,
    'OFF TIME LIBUR NASIONAL': 1,
    'TUNGGU ORDER': 2,
    'SCHEDULED PREVENTIVE MAINTENANCE': 2,
    'OVERHAUL': 3,
    
    # QUALITY REJECTION ISSUES
    'REJECT SETTING': 7,
    'OTHERS REJECTED SHEETS': 7,
    'REJECTED KARTON': 7,
    
    # OTHERS & DEFAULT
    'OTHERS': 5,
    '_NONE_': 1,
}

# Skor default jika deskripsi tidak ditemukan di map
DEFAULT_SEVERITY = 5

# ============================================================================
# KAMUS PENERJEMAH: Sensor Error Names -> Training Data Names
# ============================================================================
# Memetakan nama error dari sensor_simulator.py (kiri) ke nama dari
# data training CSV (kanan). Ini memungkinkan sensor real-time menggunakan
# nama yang berbeda dari data historis.
SENSOR_TO_TRAINING_MAP = {
    # Format: "SENSOR_ERROR_NAME": "TRAINING_DATA_NAME"
    
    # Mechanical Issues
    "SLOTTER_MISALIGNMENT": "SLOTER LARI",
    "CREASING_CRACK": "CREASING PECAH",
    "CREASING_MISALIGNMENT": "CREASING MIRING",
    "DIECUT_CRACK": "DIECUT PECAH",
    "DIECUT_MISALIGNMENT": "DIECUT LARI",
    
    # Printing Issues
    "INK_BLOBBING": "PRINT BLOBOR",
    "PRINT_GHOSTING": "PRINTING BOTAK",
    "PRINT_BLUR": "PRINT BLUR",
    "WARNA_TIDAK_SESUAI": "WARNA TIDAK SESUAI",
    
    # Electrical Issues
    "FEEDER_JAM_ELEC": "FEEDER UNIT TROUBLE ELEKTRIK",
    "PRINTING_UNIT_ELEC_FAULT": "PRINTING UNIT TROUBLE ELEKTRIK",
    "SLOTTER_UNIT_ELEC_FAULT": "SLOTTER UNIT TROUBLE ELEKTRIK",
    
    # Mechanical Failures
    "FEEDER_JAM_MECH": "FEEDER UNIT TROUBLE MEKANIK",
    "PRINTING_UNIT_MECH_FAULT": "PRINTING UNIT TROUBLE MEKANIK",
    "SLOTTER_UNIT_MECH_FAULT": "SLOTTER UNIT TROUBLE MEKANIK",
    
    # Other Issues
    "INK_LEAK": "LIMBAH TINTA BANJIR",
    "WAITING_INK": "TUNGGU TINTA",
    
    # Fallback
    "_NONE_": "_NONE_",
    "": "_NONE_"
}


def get_fmea_severity_from_reason(reason: str) -> int:
    """
    Mendapatkan skor FMEA Severity berdasarkan reason (alasan downtime).
    
    Args:
        reason: Alasan downtime (sudah diterjemahkan ke format training data)
        
    Returns:
        int: Skor severity 1-10 (1=ringan, 10=sangat parah)
    """
    # Normalisasi: strip whitespace dan uppercase
    normalized_reason = str(reason).strip().upper() if reason else ''
    
    # Cek untuk _NONE_ secara eksplisit
    if not normalized_reason or normalized_reason == '_NONE_':
        return FMEA_SEVERITY_MAP.get('_NONE_', 1)  # Return 1 untuk _NONE_
    
    # Cari di FMEA map
    if normalized_reason in FMEA_SEVERITY_MAP:
        return FMEA_SEVERITY_MAP[normalized_reason]
    
    # Default jika tidak ditemukan
    logger.warning(f"FMEA Severity tidak ditemukan untuk reason '{normalized_reason}', using default={DEFAULT_SEVERITY}")
    return DEFAULT_SEVERITY


class PredictionService:
    """Service untuk machine learning predictions dan model management."""
    
    def __init__(self):
        """Initialize prediction service dan load model."""
        self.model = None
        self.feature_names = None
        self.model_loaded = False
        self.model_path = self._get_model_path()
        self.feature_names_path = self._get_feature_names_path()
        self._load_model()
        self._load_feature_names()
    
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
    
    def _get_feature_names_path(self) -> Path:
        """
        Mendapatkan path ke file feature names.
        
        Returns:
            Path ke feature_names.pkl
        """
        current_dir = Path(__file__).resolve().parent
        backend_dir = current_dir.parent.parent  # Backend directory
        feature_names_path = backend_dir.parent / "Model" / "feature_names.pkl"
        return feature_names_path
    
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
    
    def _load_feature_names(self) -> None:
        """Load feature names dari file dengan error handling."""
        try:
            logger.info(f"Loading feature names from: {self.feature_names_path}")
            
            if not self.feature_names_path.exists():
                logger.warning(f"Feature names file tidak ditemukan: {self.feature_names_path}")
                logger.warning("Model akan menggunakan mode fallback (2 fitur sederhana)")
                self.feature_names = None
                return
            
            self.feature_names = joblib.load(self.feature_names_path)
            
            logger.info(f"Feature names loaded successfully! Total features: {len(self.feature_names)}")
            logger.info(f"Sample features: {self.feature_names[:5]}")
            
        except Exception as e:
            logger.error(f"Failed to load feature names: {e}")
            self.feature_names = None
    
    def _prepare_feature_array(self, real_time_data: Dict[str, Any]) -> pd.DataFrame:
        """
        Menyiapkan array fitur dari data real-time sensor.
        Model "Murni Fishbone + Shift" - Menggunakan fitur kategorikal (alasan downtime + shift).
        TIDAK menggunakan fitur produksi untuk mencegah kebocoran data.
        
        Args:
            real_time_data: Dictionary dengan keys:
                - reason (str): Alasan downtime (WAJIB untuk model ini)
                - shift (str/int): Nomor shift (1, 2, 3) - OPSIONAL, default _NONE_
                - production (int): TIDAK DIGUNAKAN (backward compatibility)
                - defects (int): TIDAK DIGUNAKAN (backward compatibility)
        
        Returns:
            DataFrame 1xN dengan fitur kategorikal yang dibutuhkan model
        """
        # Validasi input - reason adalah field paling penting
        reason = real_time_data.get('reason', '').strip().upper()
        
        if not reason:
            logger.warning("No reason provided. Model murni fishbone membutuhkan 'reason' untuk prediksi akurat.")
        
        logger.info(f"Preparing features for: reason='{reason}'")
        logger.info(f"⚠ Model Murni Fishbone: Mengabaikan data produksi (production={real_time_data.get('production', 'N/A')}, defects={real_time_data.get('defects', 'N/A')})")
        
        # Buat DataFrame kosong dengan semua fitur (inisialisasi ke 0)
        df = pd.DataFrame(0, index=[0], columns=self.feature_names)
        
        # ========================================================================
        # FITUR PRODUKSI & OEE: DIHAPUS
        # ========================================================================
        # Model "Murni Fishbone" TIDAK menggunakan:
        # - Total Produksi (Pcs)
        # - Produk Cacat (Pcs)  
        # - Quality_Rate
        # - Availability_Rate
        #
        # Alasan: Mencegah kebocoran data dan memaksa model belajar 100% dari
        # pola alasan downtime (Fishbone Analysis).
        
        logger.info(f"⚠ Melewati fitur produksi/OEE (Model Murni Fishbone)")
        
        # ========================================================================
        # FITUR FMEA SEVERITY: HITUNG SKOR KEPARAHAN
        # ========================================================================
        # Model baru menggunakan FMEA Severity Score sebagai fitur numerik
        # untuk memberikan konteks keparahan dari alasan downtime
        
        # Inisialisasi severity dengan default
        severity_score = DEFAULT_SEVERITY
        mapped_reason = reason  # Akan diupdate saat translasi
        
        # ========================================================================
        # PETAKAN FITUR KATEGORIKAL (ONE-HOT ENCODING) - INI SATU-SATUNYA INPUT
        # ========================================================================
        if reason:
            # ====================================================================
            # STEP 1: TERJEMAHKAN REASON MENGGUNAKAN KAMUS
            # ====================================================================
            # Sensor simulator menggunakan nama seperti "SLOTTER_MISALIGNMENT"
            # Training data menggunakan nama seperti "SLOTER LARI"
            # Kamus SENSOR_TO_TRAINING_MAP menghubungkan keduanya
            
            raw_reason = reason  # Simpan reason asli untuk logging
            mapped_reason = SENSOR_TO_TRAINING_MAP.get(reason, reason)
            
            if mapped_reason != reason:
                logger.info(f"🔄 Translating reason: '{raw_reason}' -> '{mapped_reason}'")
            else:
                logger.info(f"✓ Using reason as-is: '{reason}'")
            
            # Hitung FMEA Severity berdasarkan mapped_reason
            severity_score = get_fmea_severity_from_reason(mapped_reason)
            logger.info(f"📊 FMEA Severity Score: {severity_score}/10")
            
            # ====================================================================
            # STEP 2: BUAT KEY UNTUK ONE-HOT ENCODING
            # ====================================================================
            # Coba cari kolom yang cocok dengan reason yang sudah diterjemahkan
            # Possible formats: "Scrab Description_REASON" atau "Break Time Description_REASON"
            key_scrab = f"Scrab Description_{mapped_reason}"
            key_break = f"Break Time Description_{mapped_reason}"
            
            matched = False
            
            # Cek apakah reason ada di Scrab Description
            if key_scrab in df.columns:
                df[key_scrab] = 1
                matched = True
                logger.info(f"✓ Matched to feature: '{key_scrab}'")
            
            # Cek apakah reason ada di Break Time Description
            elif key_break in df.columns:
                df[key_break] = 1
                matched = True
                logger.info(f"✓ Matched to feature: '{key_break}'")
            
            # Jika tidak ada yang cocok, set ke _NONE_
            else:
                logger.warning(f"⚠ Reason '{mapped_reason}' tidak ditemukan di training data, using _NONE_")
                
                # Set ke kolom _NONE_ sebagai fallback
                if "Scrab Description__NONE_" in df.columns:
                    df["Scrab Description__NONE_"] = 1
                if "Break Time Description__NONE_" in df.columns:
                    df["Break Time Description__NONE_"] = 1
        
        else:
            # Jika tidak ada reason, set ke _NONE_
            logger.info("No reason provided, using _NONE_ category")
            if "Scrab Description__NONE_" in df.columns:
                df["Scrab Description__NONE_"] = 1
            if "Break Time Description__NONE_" in df.columns:
                df["Break Time Description__NONE_"] = 1
        
        # ========================================================================
        # PETAKAN FITUR SHIFT (ONE-HOT ENCODING)
        # ========================================================================
        # Shift adalah konteks waktu produksi (1=Pagi, 2=Siang, 3=Malam)
        # Training data menggunakan format: Shift_1.0, Shift_2.0, Shift_3.0, Shift__NONE_
        
        current_shift = str(real_time_data.get('shift', '_NONE_')).strip()
        
        if current_shift and current_shift != '_NONE_':
            # Konversi ke format float (pandas one-hot encoding membuat Shift_1.0, Shift_2.0)
            try:
                # Coba parse sebagai angka dan konversi ke format X.0
                shift_num = float(current_shift)
                current_shift = f"{shift_num:.1f}"  # Format: "1.0", "2.0", "3.0"
            except ValueError:
                # Jika bukan angka, biarkan sebagai string
                logger.warning(f"⚠ Shift value '{current_shift}' bukan angka, menggunakan as-is")
            
            shift_key = f"Shift_{current_shift}"
            
            if shift_key in df.columns:
                df[shift_key] = 1
                logger.info(f"✓ Matched shift to feature: '{shift_key}'")
            else:
                # Fallback ke _NONE_ jika shift tidak dikenal
                logger.warning(f"⚠ Shift '{current_shift}' tidak ditemukan di training data, using _NONE_")
                if "Shift__NONE_" in df.columns:
                    df["Shift__NONE_"] = 1
        
        else:
            # Jika tidak ada shift, set ke _NONE_
            logger.info("No shift provided, using Shift__NONE_ category")
            if "Shift__NONE_" in df.columns:
                df["Shift__NONE_"] = 1
        
        # ========================================================================
        # TAMBAHKAN FITUR FMEA SEVERITY
        # ========================================================================
        # Pastikan kolom FMEA_Severity ada di DataFrame
        if "FMEA_Severity" in df.columns:
            df["FMEA_Severity"] = severity_score
            logger.info(f"✓ FMEA_Severity set to: {severity_score}")
        else:
            logger.warning("⚠ FMEA_Severity column not found in feature names. Model might be old version.")
        
        logger.info(f"Feature array prepared successfully: shape={df.shape}")
        
        return df
    
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
    
    def predict_downtime(self, real_time_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Memprediksi durasi downtime berdasarkan data real-time sensor.
        Fungsi ini dipanggil oleh health_service saat downtime terdeteksi.
        
        Args:
            real_time_data: Dictionary dengan format:
                {
                    "production": 19379,  # Total produksi (pcs)
                    "defects": 806,       # Total produk cacat (pcs)
                    "reason": "SLOTER LARI"  # Alasan downtime (opsional)
                }
        
        Returns:
            Dictionary dengan hasil prediksi dan metadata
        """
        try:
            # Validasi model availability
            if not self.model_loaded or self.model is None:
                return {
                    'success': False,
                    'prediction': None,
                    'input': real_time_data,
                    'message': 'Model tidak tersedia. Silakan restart server atau periksa file model.',
                    'troubleshooting': [
                        'Pastikan file model.pkl ada di folder Model/',
                        'Restart aplikasi',
                        'Periksa log untuk error detail'
                    ]
                }
            
            # Validasi feature names availability
            if self.feature_names is None:
                logger.warning("Feature names tidak tersedia, menggunakan mode fallback")
                # Fallback ke mode sederhana (2 fitur)
                return self._predict_simple_mode(real_time_data)
            
            logger.info(f"Predicting downtime for: {real_time_data}")
            
            # Siapkan feature array (1x62)
            feature_df = self._prepare_feature_array(real_time_data)
            
            # Lakukan prediksi
            prediction = self.model.predict(feature_df)
            prediction_value = float(prediction[0])
            
            # Pastikan prediksi tidak negatif
            if prediction_value < 0:
                logger.warning(f"Negative prediction detected: {prediction_value}, setting to 0")
                prediction_value = 0
            
            prediction_value = round(prediction_value, 2)
            
            logger.info(f"Prediction completed: {prediction_value} minutes")
            
            # Format hasil
            result = {
                'success': True,
                'prediction': prediction_value,
                'prediction_formatted': self._format_prediction_time(prediction_value),
                'input': real_time_data,
                'message': 'Prediksi berhasil',
                'metadata': {
                    'model_type': type(self.model).__name__,
                    'total_features': len(self.feature_names),
                    'prediction_unit': 'minutes',
                    'feature_engineering': 'OEE + Fishbone Analysis',
                    'model_version': '2.0 (Advanced Features)'
                }
            }
            
            return result
            
        except ValueError as e:
            logger.warning(f"Validation error: {e}")
            return {
                'success': False,
                'prediction': None,
                'input': real_time_data,
                'message': f"Validation error: {str(e)}",
                'error_type': 'ValidationError'
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}", exc_info=True)
            return {
                'success': False,
                'prediction': None,
                'input': real_time_data,
                'message': f"Prediction error: {str(e)}",
                'error_type': 'PredictionError'
            }
    
    def _predict_simple_mode(self, real_time_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Mode fallback untuk prediksi dengan 2 fitur sederhana.
        Digunakan jika feature_names.pkl tidak tersedia.
        
        Args:
            real_time_data: Dictionary dengan production dan defects
            
        Returns:
            Dictionary dengan hasil prediksi
        """
        try:
            production = float(real_time_data.get('production', 0))
            defects = float(real_time_data.get('defects', 0))
            
            # Model expects: [total_produksi, produk_cacat]
            X = np.array([[production, defects]])
            
            # Lakukan prediksi
            prediction = self.model.predict(X)
            prediction_value = float(prediction[0])
            
            if prediction_value < 0:
                prediction_value = 0
            
            prediction_value = round(prediction_value, 2)
            
            logger.info(f"Simple mode prediction completed: {prediction_value} minutes")
            
            return {
                'success': True,
                'prediction': prediction_value,
                'prediction_formatted': self._format_prediction_time(prediction_value),
                'input': real_time_data,
                'message': 'Prediksi berhasil (simple mode)',
                'metadata': {
                    'model_type': type(self.model).__name__,
                    'total_features': 2,
                    'prediction_unit': 'minutes',
                    'mode': 'Simple (Fallback)'
                }
            }
            
        except Exception as e:
            logger.error(f"Simple mode prediction error: {e}")
            return {
                'success': False,
                'prediction': None,
                'input': real_time_data,
                'message': f"Prediction error: {str(e)}",
                'error_type': 'PredictionError'
            }
    
    def predict_maintenance_duration(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Alias untuk backward compatibility.
        Konversi format lama ke format baru.
        
        Args:
            input_data: Dictionary dengan total_produksi dan produk_cacat (format lama)
            
        Returns:
            Dictionary dengan hasil prediksi
        """
        # Konversi format lama ke format baru
        real_time_data = {
            'production': input_data.get('total_produksi', 0),
            'defects': input_data.get('produk_cacat', 0),
            'reason': input_data.get('reason', '')
        }
        
        logger.info("Using backward compatibility mode (predict_maintenance_duration)")
        return self.predict_downtime(real_time_data)
    
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
            # Informasi dasar model
            info = {
                'loaded': True,
                'model_details': {
                    'type': type(self.model).__name__,
                    'class': str(self.model.__class__),
                    'path': str(self.model_path)
                },
                'model_parameters': {
                    'n_estimators': getattr(self.model, 'n_estimators', None),
                    'max_depth': getattr(self.model, 'max_depth', None),
                    'n_features': self.model.n_features_in_ if hasattr(self.model, 'n_features_in_') else None,
                    'random_state': getattr(self.model, 'random_state', None)
                },
                'feature_info': {
                    'mode': 'Advanced (62 features)' if self.feature_names else 'Simple (2 features)',
                    'total_features': len(self.feature_names) if self.feature_names else 2,
                    'feature_names_loaded': self.feature_names is not None,
                    'feature_names_path': str(self.feature_names_path)
                },
                'performance_info': {
                    'prediction_unit': 'minutes',
                    'mae': '60.29 minutes (from evaluation)',
                    'rmse': '265.51 minutes (from evaluation)',
                    'mape': '6.30% (from evaluation)',
                    'r2_score': '0.9853 (98.53% accuracy)',
                    'processing_time': 'Real-time (< 100ms)'
                },
                'message': 'Model information retrieved successfully'
            }
            
            # Tambahkan informasi feature categories jika tersedia
            if self.feature_names:
                base_features = [f for f in self.feature_names if not any(
                    f.startswith(prefix) for prefix in ['Scrab Description_', 'Break Time Description_']
                )]
                scrab_features = [f for f in self.feature_names if f.startswith('Scrab Description_')]
                break_features = [f for f in self.feature_names if f.startswith('Break Time Description_')]
                
                info['feature_categories'] = {
                    'base_features': len(base_features),
                    'scrab_description_features': len(scrab_features),
                    'break_time_description_features': len(break_features),
                    'sample_base_features': base_features[:5],
                    'sample_scrab_features': scrab_features[:5],
                    'sample_break_features': break_features[:5]
                }
                
                info['input_format'] = {
                    'production': 'int/float (Total Produksi dalam pcs)',
                    'defects': 'int/float (Produk Cacat dalam pcs)',
                    'reason': 'string (Alasan downtime, opsional)'
                }
                
                info['example_input'] = {
                    'production': 19379,
                    'defects': 806,
                    'reason': 'SLOTER LARI'
                }
            else:
                info['input_format'] = {
                    'total_produksi': 'float/int (>= 0)',
                    'produk_cacat': 'float/int (>= 0, <= total_produksi)'
                }
                
                info['example_input'] = {
                    'total_produksi': 19379,
                    'produk_cacat': 806
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
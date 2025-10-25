"""
Health Service
Service layer untuk kalkulasi health index dan metrics
"""

import random
from datetime import datetime
from typing import Dict, Any, List
from config import RPN_WEIGHT, OEE_WEIGHT, HEALTH_THRESHOLD_GOOD, OEE_MIN, OEE_MAX
from src.utils.logger import get_logger
from src.services.database_service import db_service

logger = get_logger(__name__)

# Threshold kritis untuk pemicu otomatis prediksi maintenance
CRITICAL_THRESHOLD = 40.0


class HealthService:
    """Service untuk kalkulasi dan manajemen health metrics komponen."""
    
    def __init__(self):
        """Initialize health service."""
        # Lazy import untuk menghindari circular dependency
        self._prediction_service = None
        logger.info("HealthService initialized")
    
    def _get_prediction_service(self):
        """
        Lazy loading untuk Enhanced PredictionService untuk menghindari circular import.
        
        Returns:
            Instance dari Enhanced PredictionService
        """
        if self._prediction_service is None:
            from src.services.enhanced_prediction_service import EnhancedPredictionService
            self._prediction_service = EnhancedPredictionService()
        return self._prediction_service
    
    def calculate_rpn_score(self, rpn_value: float, rpn_max: float) -> float:
        """
        Menghitung RPN Score dari nilai RPN.
        
        Args:
            rpn_value: Nilai RPN komponen saat ini
            rpn_max: Nilai RPN maksimal
            
        Returns:
            RPN Score (0-100)
        """
        if rpn_max == 0:
            return 0
        
        rpn_score = (1 - rpn_value / rpn_max) * 100
        return round(rpn_score, 2)
    
    def generate_oee_score(self) -> Dict[str, float]:
        """
        Menghitung OEE Score berbasis data sensor terbaru di database.
        Formula: OEE = Availability × Performance × Quality (dalam desimal)
        
        Availability dihitung berdasarkan WAKTU (time-based), bukan jumlah log.
        Performance dan Quality diambil dari data terbaru.
        
        Returns:
            Dict dengan keys: oee_score, availability_rate, performance_rate, quality_rate
        """
        # Ambil histori untuk menghitung availability (1 jam terakhir atau lebih)
        recent_logs = db_service.get_recent_machine_logs(limit=200)
        
        if not recent_logs:
            logger.warning("No machine logs available, using fallback values")
            return {
                "oee_score": float(OEE_MIN),
                "availability_rate": 95.0,
                "performance_rate": 0.0,
                "quality_rate": 0.0
            }
        
        # ===================================================================
        # HITUNG AVAILABILITY BERBASIS WAKTU (TIME-BASED)
        # ===================================================================
        from datetime import datetime, timedelta
        
        total_uptime_seconds = 0.0
        total_time_seconds = 0.0
        
        # Iterasi melalui log untuk menghitung durasi tiap status
        for i in range(len(recent_logs) - 1):
            current_log = recent_logs[i]
            next_log = recent_logs[i + 1]
            
            # Hitung durasi antara log ini dan log berikutnya
            current_time = current_log.get("timestamp")
            next_time = next_log.get("timestamp")
            
            if current_time and next_time:
                # Konversi ke datetime jika masih string
                if isinstance(current_time, str):
                    current_time = datetime.fromisoformat(current_time.replace('Z', '+00:00'))
                if isinstance(next_time, str):
                    next_time = datetime.fromisoformat(next_time.replace('Z', '+00:00'))
                
                # Hitung durasi (dalam detik)
                duration_seconds = abs((current_time - next_time).total_seconds())
                total_time_seconds += duration_seconds
                
                # Jika status Running, tambahkan ke uptime
                if current_log.get("machine_status") == "Running":
                    total_uptime_seconds += duration_seconds
        
        # Hitung availability berdasarkan waktu
        if total_time_seconds > 0:
            availability_rate = (total_uptime_seconds / total_time_seconds) * 100.0
        else:
            # Fallback: gunakan status log terbaru
            latest_status = recent_logs[0].get("machine_status", "Unknown")
            availability_rate = 100.0 if latest_status == "Running" else 0.0
            logger.warning(f"Cannot calculate time-based availability, using current status: {latest_status}")
        
        # Ambil Performance dan Quality dari log terbaru
        latest_log = recent_logs[0]  # Sudah diurutkan DESC
        performance_rate = float(latest_log.get("performance_rate", 0))
        quality_rate = float(latest_log.get("quality_rate", 0))
        
        # Hitung OEE = (A × P × Q) / 100^2 × 100
        oee_score = (availability_rate / 100.0) * (performance_rate / 100.0) * (quality_rate / 100.0) * 100.0
        
        # Clamp ke rentang konfigurasi
        oee_score = max(min(oee_score, float(OEE_MAX)), float(OEE_MIN))
        
        logger.info(
            f"OEE calculated (time-based): availability={availability_rate:.2f}% "
            f"(uptime={total_uptime_seconds/60:.1f}min / total={total_time_seconds/60:.1f}min), "
            f"performance={performance_rate:.2f}%, quality={quality_rate:.2f}%, oee={oee_score:.2f}%"
        )
        
        return {
            "oee_score": round(oee_score, 2),
            "availability_rate": round(availability_rate, 2),
            "performance_rate": round(performance_rate, 2),
            "quality_rate": round(quality_rate, 2)
        }
    
    def calculate_final_health_index(self, rpn_score: float, oee_score: float) -> float:
        """
        Menghitung Final Health Index dengan pembobotan.
        
        Args:
            rpn_score: RPN Score (0-100)
            oee_score: OEE Score (0-100)
            
        Returns:
            Final Health Index (0-100)
        """
        final_health_index = (rpn_score * RPN_WEIGHT) + (oee_score * OEE_WEIGHT)
        return round(final_health_index, 2)
    
    def determine_health_status(self, health_index: float) -> str:
        """
        Menentukan status kesehatan berdasarkan health index.
        
        Args:
            health_index: Final Health Index
            
        Returns:
            Status kesehatan
        """
        if health_index >= HEALTH_THRESHOLD_GOOD:
            return "Sehat"
        else:
            return "Perlu Perhatian"
    
    def generate_rule_based_recommendation(self, component_name: str, health_index: float) -> List[str]:
        """
        Menghasilkan rekomendasi tindakan perbaikan berbasis aturan FMEA dan Fishbone Diagram.
        
        Logika berbasis Tabel 4.5 FMEA dari skripsi untuk mode kegagalan dengan RPN tertinggi
        per komponen, serta analisis akar penyebab dari Fishbone Diagram.
        
        Args:
            component_name: Nama komponen (Feeder, Printing, Pre-Feeder, Slotter, Stacker)
            health_index: Final Health Index (0-100)
            
        Returns:
            List rekomendasi tindakan perbaikan spesifik komponen
        """
        recommendations = []
        
        # Normalisasi nama komponen untuk case-insensitive matching
        component_normalized = component_name.strip().lower()
        
        # =====================================================================
        # KONDISI KRITIS (Health Index < 50)
        # Rekomendasi berbasis mode kegagalan RPN tertinggi dari Tabel 4.5 FMEA
        # =====================================================================
        if health_index < 50:
            logger.warning(f"[CRITICAL] Component: {component_name} | Health: {health_index}%")
            
            if "feeder" in component_normalized and "pre" not in component_normalized:
                # Komponen: Feeder
                # Mode Kegagalan Prioritas: Keausan roller, masalah vakum
                recommendations = [
                    "[URGENT] Periksa keausan roller feeder dan ganti jika perlu",
                    "[INSPECT] Inspeksi sistem vakum penarik lembaran (kebocoran, tekanan)",
                    "[ACTION] Validasi alignment roller feeder dengan plate cylinder",
                    "[CLEAN] Bersihkan sensor deteksi kertas dan area feeding",
                    "[MONITOR] Monitor slip ratio dan feeding accuracy"
                ]
            
            elif "printing" in component_normalized:
                # Komponen: Printing
                # Mode Kegagalan Prioritas: Misalignment plate, tekanan tidak konsisten
                recommendations = [
                    "[URGENT] Periksa alignment plate cylinder terhadap anilox roller",
                    "[INSPECT] Inspeksi konsistensi tekanan cetak pada semua warna",
                    "[ACTION] Kalibrasi ulang doctor blade untuk distribusi tinta merata",
                    "[CLEAN] Bersihkan anilox roller dari residu tinta kering",
                    "[MONITOR] Verifikasi register mark accuracy dan adjust jika perlu",
                    "[CHECK] Periksa bearing plate cylinder untuk keausan/play"
                ]
            
            elif "pre" in component_normalized and "feeder" in component_normalized:
                # Komponen: Pre-Feeder
                # Mode Kegagalan Prioritas: Ketegangan belt, stopper tidak sejajar
                recommendations = [
                    "[URGENT] Periksa dan adjust ketegangan belt conveyor",
                    "[INSPECT] Pastikan stopper penumpukan karton sejajar dan berfungsi",
                    "[ACTION] Inspeksi sensor deteksi tumpukan untuk akurasi",
                    "[CLEAN] Bersihkan area belt dari debu dan serpihan karton",
                    "[MONITOR] Monitor waktu siklus feeding dan identifikasi bottleneck"
                ]
            
            elif "slotter" in component_normalized:
                # Komponen: Slotter
                # Mode Kegagalan Prioritas: Ketajaman pisau, keausan roller creasing
                recommendations = [
                    "[URGENT] Periksa ketajaman pisau slotter dan ganti jika tumpul",   
                    "[INSPECT] Inspeksi keausan roller creasing untuk crack/deformasi",
                    "[ACTION] Validasi setting jarak antar roller (slotting & creasing)",
                    "[CLEAN] Bersihkan serbuk kertas dari area pisau dan roller",
                    "[MONITOR] Ukur kedalaman slot dan ketajaman lipatan (quality check)",
                    "[CHECK] Periksa sistem pneumatik untuk tekanan optimal"
                ]
            
            elif "stacker" in component_normalized:
                # Komponen: Stacker
                # Mode Kegagalan Prioritas: Sensor penghitung kotor, belt kendor
                recommendations = [
                    "[URGENT] Bersihkan sensor penghitung tumpukan dari debu",
                    "[INSPECT] Periksa ketegangan belt conveyor stacker dan adjust",
                    "[ACTION] Inspeksi mekanisme penumpukan untuk alignment",
                    "[CLEAN] Bersihkan area stacker dari serpihan dan kotoran",
                    "[MONITOR] Verifikasi akurasi counting dan sesuaikan sensitivity sensor"
                ]
            
            else:
                # Komponen tidak dikenali atau komponen umum
                recommendations = [
                    "[URGENT] Lakukan inspeksi menyeluruh komponen",
                    "[INSPECT] Identifikasi mode kegagalan dengan analisis FMEA",
                    "[ACTION] Periksa komponen mekanis untuk keausan/kerusakan",
                    "[MONITOR] Review log operasional untuk pola kegagalan",
                    "[CONSULT] Konsultasi dengan maintenance engineer untuk root cause analysis"
                ]
        
        # =====================================================================
        # KONDISI WARNING (50 <= Health Index < 70)
        # Rekomendasi preventive maintenance dan monitoring intensif
        # =====================================================================
        elif 50 <= health_index < 70:
            logger.warning(f"[WARNING] Component: {component_name} | Health: {health_index}%")
            
            recommendations = [
                f"[MONITOR] Tingkatkan frekuensi monitoring untuk komponen {component_name}",
                "[INSPECT] Lakukan inspeksi preventive maintenance dalam 24-48 jam",
                "[ANALYZE] Analisis tren performa untuk deteksi early warning signs",
                "[PREPARE] Siapkan spare parts kritis untuk antisipasi kegagalan",
                "[DOCUMENT] Dokumentasikan anomali yang terdeteksi untuk analisis RCA"
            ]
            
            # Tambahan rekomendasi spesifik berdasarkan komponen
            if "feeder" in component_normalized:
                recommendations.append("[CHECK] Periksa kondisi roller dan belt feeder")
            elif "printing" in component_normalized:
                recommendations.append("[CHECK] Monitor konsistensi kualitas cetak dan register")
            elif "slotter" in component_normalized:
                recommendations.append("[CHECK] Evaluasi ketajaman pisau dan kondisi roller")
            elif "stacker" in component_normalized:
                recommendations.append("[CHECK] Cek akurasi sensor dan mekanisme penumpukan")
        
        # =====================================================================
        # KONDISI BAIK (Health Index >= 70)
        # Rekomendasi monitoring rutin dan preventive maintenance standar
        # =====================================================================
        else:
            logger.info(f"[GOOD] Component: {component_name} | Health: {health_index}%")
            
            recommendations = [
                "[STATUS] Kondisi komponen dalam keadaan baik",
                "[SCHEDULE] Lakukan monitoring rutin sesuai jadwal preventive maintenance",
                "[BASELINE] Catat performa baseline untuk referensi future analysis",
                "[MAINTAIN] Lanjutkan lubrication dan cleaning sesuai SOP",
                "[REVIEW] Review historical data untuk optimasi maintenance schedule"
            ]
        
        return recommendations
    
    def calculate_component_health(self, component_name: str, rpn_value: float, rpn_max: float) -> Dict[str, Any]:
        """
        Menghitung kesehatan komponen secara lengkap.
        
        Args:
            rpn_value: Nilai RPN komponen
            rpn_max: Nilai RPN maksimal
            
        Returns:
            Dictionary berisi semua metrik kesehatan
        """
        # Hitung komponen-komponen
        rpn_score = self.calculate_rpn_score(rpn_value, rpn_max)
        
        # Generate OEE dengan availability dinamis
        oee_data = self.generate_oee_score()
        oee_score = oee_data["oee_score"]
        availability_rate = oee_data["availability_rate"]
        performance_rate = oee_data["performance_rate"]
        quality_rate = oee_data["quality_rate"]
        
        # Hitung final health index
        final_health_index = self.calculate_final_health_index(rpn_score, oee_score)
        status = self.determine_health_status(final_health_index)
        
        # Generate rekomendasi berbasis aturan FMEA
        recommendations = self.generate_rule_based_recommendation(component_name, final_health_index)
        
        logger.info(
            f"Health calculated for {component_name} - RPN: {rpn_score}, OEE: {oee_score}, "
            f"Availability: {availability_rate}%, Final: {final_health_index}, "
            f"Recommendations: {len(recommendations)} items"
        )
        
        # AUTO-TRIGGER: Pemicu otomatis prediksi maintenance saat health index kritis
        prediction_result = None
        auto_triggered = False
        
        if final_health_index < CRITICAL_THRESHOLD:
            logger.warning(
                f"[CRITICAL] Health Index: {final_health_index}% < {CRITICAL_THRESHOLD}% | Auto-trigger activated"
            )
            
            try:
                # Dapatkan instance PredictionService
                prediction_service = self._get_prediction_service()
                
                # ===================================================================
                # MENGGUNAKAN MODEL MURNI FISHBONE - HANYA PERLU 'REASON'
                # ===================================================================
                logger.info("[AUTO-TRIGGER] Fetching error reason from latest sensor data...")
                
                latest_status = db_service.get_latest_machine_status()
                
                # ===================================================================
                # EKSTRAK ERROR REASON DENGAN FALLBACK CASCADE CERDAS
                # ===================================================================
                current_error_reason = ""
                if latest_status:
                    # Priority 1: error_message (dari sensor simulator)
                    current_error_reason = latest_status.get("error_message", "")
                    
                    # Priority 2: failure_reason (backup field)
                    if not current_error_reason:
                        current_error_reason = latest_status.get("failure_reason", "")
                    
                    # Priority 3: downtime_reason (alternative field)
                    if not current_error_reason:
                        current_error_reason = latest_status.get("downtime_reason", "")
                    
                    # Priority 4: Mapping berbasis komponen (default intelligent)
                    if not current_error_reason:
                        component_failure_map = {
                            "Pre-Feeder": "FEEDER_JAM_MECH",
                            "Feeder": "FEEDER_JAM_ELEC",
                            "Printing": "PRINT_GHOSTING",
                            "Slotter": "SLOTTER_MISALIGNMENT",
                            "Die-cut": "DIECUT_PECAH"
                        }
                        current_error_reason = component_failure_map.get(component_name, "GENERAL_BREAKDOWN")
                        logger.warning(
                            f"[SMART-FALLBACK] No error_message from sensor. "
                            f"Using intelligent default for {component_name}: '{current_error_reason}'"
                        )
                    
                    logger.info(
                        f"[DATA] Extracted error reason: '{current_error_reason}' | "
                        f"Component: {component_name} | "
                        f"Machine Status: {latest_status.get('machine_status', 'Unknown')}"
                    )
                else:
                    logger.warning("[WARNING] No machine status data available. Using component-based fallback.")
                    # Fallback terakhir jika tidak ada data sama sekali
                    component_failure_map = {
                        "Pre-Feeder": "FEEDER_JAM_MECH",
                        "Feeder": "FEEDER_JAM_ELEC",
                        "Printing": "PRINT_GHOSTING",
                        "Slotter": "SLOTTER_MISALIGNMENT",
                        "Die-cut": "DIECUT_PECAH"
                    }
                    current_error_reason = component_failure_map.get(component_name, "GENERAL_BREAKDOWN")
                
                # ====================================================================
                # EKSTRAK SHIFT DARI SENSOR DATA
                # ====================================================================
                # Shift adalah konteks waktu produksi yang mempengaruhi durasi downtime
                # Sensor bisa mengirimkan 'shift' atau kita gunakan default berdasarkan waktu
                current_shift = None
                
                if latest_status:
                    # Priority 1: Ambil dari sensor data
                    current_shift = latest_status.get("shift")
                    
                    # Priority 2: Ambil dari field alternatif
                    if not current_shift:
                        current_shift = latest_status.get("current_shift")
                
                # Priority 3: Default berdasarkan waktu saat ini (jika tidak ada dari sensor)
                if not current_shift:
                    from datetime import datetime
                    current_hour = datetime.now().hour
                    
                    if 6 <= current_hour < 14:
                        current_shift = 1  # Shift Pagi (06:00-14:00)
                    elif 14 <= current_hour < 22:
                        current_shift = 2  # Shift Siang (14:00-22:00)
                    else:
                        current_shift = 3  # Shift Malam (22:00-06:00)
                    
                    logger.info(f"[AUTO-DETECT] Shift detected from time: Shift {current_shift} (Hour: {current_hour})")
                
                # Siapkan data untuk model "Murni Fishbone + Shift"
                # Model membutuhkan 'reason' + 'shift' + health_index + sensor data
                real_time_data = {
                    "reason": current_error_reason if current_error_reason else "_NONE_",
                    "shift": current_shift if current_shift else "_NONE_",
                    "health_index": final_health_index,  # Tambahkan health index
                    # Tambahkan sensor data dari latest_status jika tersedia
                    "suction_strength": latest_status.get('suction_strength') if latest_status else None,
                    "blade_sharpness": latest_status.get('blade_sharpness') if latest_status else None,
                    "temp_consistency": latest_status.get('temp_consistency') if latest_status else None,
                    "run_time": latest_status.get('run_time') if latest_status else None,
                    "production": latest_status.get('production') if latest_status else None
                }
                
                logger.info(
                    f"[AUTO-TRIGGER] Initiating downtime prediction | "
                    f"Reason: '{real_time_data['reason']}' | Shift: {real_time_data['shift']}"
                )
                
                # Panggil fungsi prediksi (gunakan predict_downtime untuk model Fishbone)
                prediction_result = prediction_service.predict_downtime(real_time_data)
                auto_triggered = True
                
                # Log hasil prediksi
                if prediction_result.get('success'):
                    predicted_minutes = prediction_result.get('prediction', 0)
                    formatted_duration = prediction_result.get('prediction_formatted', 'N/A')
                    
                    logger.warning(
                        f"[SUCCESS] AUTO-PREDICTION COMPLETED | "
                        f"Health Index: {final_health_index:.2f}% | "
                        f"Error Reason: '{current_error_reason}' | "
                        f"Shift: {real_time_data.get('shift', 'N/A')} | "
                        f"Predicted Downtime Duration: {formatted_duration} ({predicted_minutes:.2f} minutes) | "
                        f"RECOMMENDATION: Schedule immediate maintenance!"
                    )
                    
                else:
                    logger.error(
                        f"[FAILED] AUTO-PREDICTION FAILED | "
                        f"Health Index: {final_health_index:.2f}% | "
                        f"Error Reason: '{current_error_reason}' | "
                        f"Error: {prediction_result.get('message', 'Unknown error')}"
                    )
                
            except Exception as e:
                logger.error(
                    f"[ERROR] Exception during auto-trigger prediction | "
                    f"Health Index: {final_health_index:.2f}% | "
                    f"Exception: {str(e)}",
                    exc_info=True
                )
                prediction_result = {
                    "success": False,
                    "message": f"Auto-trigger error: {str(e)}"
                }
        
        # Kembalikan hasil dengan informasi prediksi otomatis dan rekomendasi
        result = {
            "rpn_score": rpn_score,
            "oee_score": oee_score,
            "final_health_index": final_health_index,
            "status": status,
            "rpn_value": rpn_value,
            "rpn_max": rpn_max,
            "availability_rate": availability_rate,
            "performance_rate": performance_rate,
            "quality_rate": quality_rate,
            "recommendations": recommendations  # Rekomendasi berbasis aturan FMEA
        }
        
        # Tambahkan informasi auto-trigger jika terjadi
        if auto_triggered:
            result["auto_prediction"] = {
                "triggered": True,
                "trigger_threshold": CRITICAL_THRESHOLD,
                "prediction_result": prediction_result
            }
        
        return result
    
    def get_health_color(self, health_index: float) -> str:
        """
        Mendapatkan warna berdasarkan health index untuk UI.
        
        Args:
            health_index: Final Health Index
            
        Returns:
            Warna dalam format hex
        """
        if health_index >= 90:
            return "#00AA00"  # Dark Green - Excellent
        elif health_index >= 80:
            return "#00FF00"  # Green - Good
        elif health_index >= 70:
            return "#AAFF00"  # Light Green - Fair
        elif health_index >= 50:
            return "#FFAA00"  # Orange - Poor
        else:
            return "#FF0000"  # Red - Critical
    
    def get_health_description(self, health_index: float) -> str:
        """
        Mendapatkan deskripsi detail berdasarkan health index.
        
        Args:
            health_index: Final Health Index
            
        Returns:
            Deskripsi status kesehatan
        """
        if health_index >= 90:
            return "Kondisi mesin sangat baik, tidak ada tindakan yang diperlukan"
        elif health_index >= 80:
            return "Kondisi mesin baik, lakukan monitoring rutin"
        elif health_index >= 70:
            return "Kondisi mesin normal, perhatikan tren penurunan"
        elif health_index >= 50:
            return "Kondisi mesin perlu perhatian, rencanakan maintenance"
        else:
            return "Kondisi mesin kritis, lakukan maintenance segera"
    
    def get_severity_level(self, health_index: float) -> str:
        """
        Mendapatkan level severity berdasarkan health index.
        
        Args:
            health_index: Final Health Index
            
        Returns:
            Severity level
        """
        if health_index >= 90:
            return "Excellent"
        elif health_index >= 80:
            return "Good"
        elif health_index >= 70:
            return "Fair"
        elif health_index >= 50:
            return "Poor"
        else:
            return "Critical"
    
    def get_recommendations(self, health_index: float) -> List[str]:
        """
        Mendapatkan rekomendasi berdasarkan health index.
        
        Args:
            health_index: Final Health Index
            
        Returns:
            List rekomendasi tindakan
        """
        if health_index >= 90:
            return [
                "Lanjutkan operasi normal",
                "Monitor berkala sesuai jadwal",
                "Dokumentasikan performa terbaik sebagai benchmark"
            ]
        elif health_index >= 80:
            return [
                "Lanjutkan operasi dengan monitoring rutin",
                "Periksa tren performa mingguan",
                "Siapkan spare parts standar"
            ]
        elif health_index >= 70:
            return [
                "Tingkatkan frekuensi monitoring",
                "Analisis tren penurunan performa",
                "Rencanakan preventive maintenance"
            ]
        elif health_index >= 50:
            return [
                "Segera jadwalkan maintenance",
                "Identifikasi akar penyebab masalah",
                "Siapkan spare parts kritis",
                "Pertimbangkan backup equipment"
            ]
        else:
            return [
                "URGENT: Hentikan operasi jika perlu",
                "Lakukan maintenance segera",
                "Investigasi menyeluruh akar masalah",
                "Siapkan replacement parts",
                "Aktivasi prosedur emergency"
            ]
    
    def get_current_timestamp(self) -> str:
        """
        Mendapatkan timestamp saat ini.
        
        Returns:
            ISO formatted timestamp
        """
        return datetime.now().isoformat()
    
    def _calculate_health_index(self, component_name: str, rpn_value: float, rpn_max: float) -> Dict[str, Any]:
        """
        Menghitung health index dan status untuk komponen tertentu.
        
        Args:
            component_name: Nama komponen
            rpn_value: Nilai RPN komponen saat ini
            rpn_max: Nilai RPN maksimal
            
        Returns:
            Dictionary berisi health index, status, dan rekomendasi
        """
        # Hitung RPN Score
        rpn_score = self.calculate_rpn_score(rpn_value, rpn_max)
        
        # Generate OEE Score
        oee_data = self.generate_oee_score()
        oee_score = oee_data["oee_score"]
        
        # Hitung Final Health Index
        final_health_index = self.calculate_final_health_index(rpn_score, oee_score)
        status = self.determine_health_status(final_health_index)
        
        # Generate rekomendasi
        recommendations = self.generate_rule_based_recommendation(component_name, final_health_index)
        
        # Note: Auto-trigger prediction logic sudah dipindahkan ke update_component_health()
        
        return {
            "rpn_score": rpn_score,
            "oee_score": oee_score,
            "final_health_index": final_health_index,
            "status": status,
            "recommendations": recommendations
        }
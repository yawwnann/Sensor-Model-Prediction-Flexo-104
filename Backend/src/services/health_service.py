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
        Lazy loading untuk PredictionService untuk menghindari circular import.
        
        Returns:
            Instance dari PredictionService
        """
        if self._prediction_service is None:
            from src.services.prediction_service import PredictionService
            self._prediction_service = PredictionService()
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
        
        Availability dihitung dari histori machine_status (Running vs Downtime).
        Performance dan Quality diambil dari data terbaru.
        
        Returns:
            Dict dengan keys: oee_score, availability_rate, performance_rate, quality_rate
        """
        # Ambil histori untuk menghitung availability
        recent_logs = db_service.get_recent_machine_logs(limit=100)
        
        if not recent_logs:
            logger.warning("No machine logs available, using fallback values")
            return {
                "oee_score": float(OEE_MIN),
                "availability_rate": 95.0,
                "performance_rate": 0.0,
                "quality_rate": 0.0
            }
        
        # Hitung Availability dari histori status
        running_count = sum(1 for log in recent_logs if log.get("machine_status") == "Running")
        total_count = len(recent_logs)
        availability_rate = (running_count / total_count) * 100.0
        
        # Ambil Performance dan Quality dari log terbaru
        latest_log = recent_logs[0]  # Sudah diurutkan DESC
        performance_rate = float(latest_log.get("performance_rate", 0))
        quality_rate = float(latest_log.get("quality_rate", 0))
        
        # Hitung OEE = (A × P × Q) / 100^2 × 100
        oee_score = (availability_rate / 100.0) * (performance_rate / 100.0) * (quality_rate / 100.0) * 100.0
        
        # Clamp ke rentang konfigurasi
        oee_score = max(min(oee_score, float(OEE_MAX)), float(OEE_MIN))
        
        logger.info(
            f"OEE calculated: availability={availability_rate:.2f}% ({running_count}/{total_count} Running), "
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
                # MENGGUNAKAN DATA KUMULATIF REAL-TIME DARI DATABASE
                # ===================================================================
                logger.info("[DATA] Fetching real-time cumulative production data from database...")
                
                latest_status = db_service.get_latest_machine_status()
                
                if latest_status and latest_status.get("cumulative_production") is not None:
                    # Gunakan data kumulatif real dari simulator
                    total_produksi = latest_status.get("cumulative_production", 0)
                    produk_cacat = latest_status.get("cumulative_defects", 0)
                    
                    logger.info(
                        f"[SUCCESS] Using REAL cumulative data from simulator | "
                        f"Production: {total_produksi} pcs | Defects: {produk_cacat} pcs"
                    )
                    
                    # Validasi data: jika production = 0, gunakan nilai minimal
                    if total_produksi == 0:
                        logger.warning("[WARNING] Cumulative production is 0 (shift just started or machine idle)")
                        total_produksi = 100  # Minimal untuk prediksi
                        produk_cacat = 5
                        logger.info(f"Using minimal values for prediction: Production={total_produksi}, Defects={produk_cacat}")
                else:
                    # Fallback: data kumulatif belum tersedia (database belum ada cumulative columns)
                    logger.warning("[WARNING] Cumulative data not available in database. Using fallback defaults.")
                    total_produksi = 4000
                    produk_cacat = 150
                
                input_data = {
                    "total_produksi": total_produksi,
                    "produk_cacat": produk_cacat
                }
                
                logger.info(f"[AUTO-TRIGGER] Initiating maintenance prediction with input: {input_data}")
                
                # Panggil fungsi prediksi
                prediction_result = prediction_service.predict_maintenance_duration(input_data)
                auto_triggered = True
                
                # Log hasil prediksi
                if prediction_result.get('success'):
                    logger.warning(
                        f"[SUCCESS] AUTO-PREDICTION COMPLETED | "
                        f"Health Index: {final_health_index} | "
                        f"Predicted Maintenance Duration: {prediction_result.get('prediction_formatted', 'N/A')} | "
                        f"Input: Total Produksi={total_produksi}, Produk Cacat={produk_cacat} | "
                        f"RECOMMENDATION: Schedule immediate maintenance!"
                    )
                else:
                    logger.error(
                        f"[FAILED] AUTO-PREDICTION FAILED | "
                        f"Health Index: {final_health_index} | "
                        f"Error: {prediction_result.get('message', 'Unknown error')}"
                    )
                
            except Exception as e:
                logger.error(
                    f"[ERROR] Exception during auto-trigger prediction | "
                    f"Health Index: {final_health_index} | "
                    f"Exception: {str(e)}"
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
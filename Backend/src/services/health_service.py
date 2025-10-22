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


class HealthService:
    """Service untuk kalkulasi dan manajemen health metrics komponen."""
    
    def __init__(self):
        """Initialize health service."""
        logger.info("HealthService initialized")
    
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
    
    def generate_oee_score(self) -> float:
        """
        Menghitung OEE Score berbasis data sensor terbaru di database.
        Formula: OEE = Availability × Performance × Quality (dalam desimal)
        
        Jika data tidak tersedia, fallback ke nilai minimum agar konservatif.
        """
        latest = db_service.get_latest_machine_status()
        if not latest:
            logger.warning("No machine status data available, using OEE_MIN fallback")
            return float(OEE_MIN)
        
        perf = latest.get("performance_rate")
        qual = latest.get("quality_rate")
        avail = latest.get("availability_rate", 95.0)  # Default availability 95%
        
        if perf is None or qual is None:
            logger.warning(f"Missing performance or quality rate: perf={perf}, qual={qual}")
            return float(OEE_MIN)
        
        # Konversi ke float
        perf = float(perf)
        qual = float(qual)
        avail = float(avail)
        
        # OEE = (Availability / 100) × (Performance / 100) × (Quality / 100) × 100
        oee_score = (avail / 100.0) * (perf / 100.0) * (qual / 100.0) * 100.0
        
        # Clamp ke rentang konfigurasi
        oee_score = max(min(oee_score, float(OEE_MAX)), float(OEE_MIN))
        
        logger.info(f"OEE calculated: avail={avail}%, perf={perf}%, qual={qual}%, oee={oee_score}%")
        return round(oee_score, 2)
    
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
    
    def calculate_component_health(self, rpn_value: float, rpn_max: float) -> Dict[str, Any]:
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
        oee_score = self.generate_oee_score()
        final_health_index = self.calculate_final_health_index(rpn_score, oee_score)
        status = self.determine_health_status(final_health_index)
        
        # Ambil semua komponen OEE dari data terbaru
        latest_data = db_service.get_latest_machine_status()
        performance_rate = 0.0
        quality_rate = 0.0
        availability_rate = 95.0  # Default availability
        
        if latest_data:
            performance_rate = float(latest_data.get("performance_rate", 0))
            quality_rate = float(latest_data.get("quality_rate", 0))
            availability_rate = float(latest_data.get("availability_rate", 95.0))
        
        logger.info(f"Health calculated - RPN: {rpn_score}, OEE: {oee_score}, Final: {final_health_index}")
        
        return {
            "rpn_score": rpn_score,
            "oee_score": oee_score,
            "final_health_index": final_health_index,
            "status": status,
            "rpn_value": rpn_value,
            "rpn_max": rpn_max,
            "availability_rate": availability_rate,
            "performance_rate": performance_rate,
            "quality_rate": quality_rate
        }
    
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
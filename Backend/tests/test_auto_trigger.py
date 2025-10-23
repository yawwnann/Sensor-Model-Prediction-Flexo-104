"""
Test untuk Auto-Prediction Trigger Feature
Test suite untuk memverifikasi pemicu otomatis prediksi maintenance
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services.health_service import HealthService, CRITICAL_THRESHOLD
from src.services.prediction_service import PredictionService
from src.utils.logger import get_logger

logger = get_logger(__name__)


def test_auto_trigger_on_critical_health():
    """
    Test 1: Verifikasi pemicu otomatis saat health index < CRITICAL_THRESHOLD
    """
    print("\n" + "="*80)
    print("TEST 1: Auto-Trigger pada Critical Health")
    print("="*80)
    
    health_service = HealthService()
    
    # Simulasi kondisi kritis: RPN tinggi (buruk) dan OEE rendah
    # RPN_MAX diasumsikan 1000, kita set RPN_VALUE sangat tinggi
    # Formula: Health = (RPN_Score * 0.4) + (OEE_Score * 0.6)
    # Untuk Health < 40: RPN tinggi + OEE rendah
    rpn_value = 950  # RPN sangat tinggi = kondisi sangat buruk (RPN Score = 5%)
    rpn_max = 1000
    
    print(f"\nInput Test:")
    print(f"  RPN Value: {rpn_value}")
    print(f"  RPN Max: {rpn_max}")
    print(f"  Expected RPN Score: {((1 - rpn_value/rpn_max) * 100):.2f}%")
    print(f"  Critical Threshold: {CRITICAL_THRESHOLD}")
    print(f"  Note: Untuk trigger, butuh OEE rendah juga (diambil dari DB)")

    
    # Hitung health
    result = health_service.calculate_component_health(rpn_value, rpn_max)
    
    print(f"\nHasil Perhitungan:")
    print(f"  Final Health Index: {result['final_health_index']}")
    print(f"  Status: {result['status']}")
    print(f"  RPN Score: {result['rpn_score']}%")
    print(f"  OEE Score: {result['oee_score']}%")
    
    # Verifikasi auto-trigger
    if result['final_health_index'] < CRITICAL_THRESHOLD:
        # Health memang di bawah threshold
        if "auto_prediction" in result:
            print(f"\n✅ AUTO-TRIGGER DETECTED!")
            print(f"  Triggered: {result['auto_prediction']['triggered']}")
            print(f"  Threshold: {result['auto_prediction']['trigger_threshold']}")
            
            pred_result = result['auto_prediction']['prediction_result']
            print(f"\n  Prediction Result:")
            print(f"    Success: {pred_result.get('success')}")
            print(f"    Duration: {pred_result.get('prediction_formatted', 'N/A')}")
            print(f"    Input: {pred_result.get('input')}")
            
            if pred_result.get('success'):
                print("\n✅ TEST PASSED: Auto-trigger berhasil dan prediksi sukses")
            else:
                print(f"\n⚠️ TEST WARNING: Auto-trigger berhasil tapi prediksi gagal: {pred_result.get('message')}")
        else:
            print(f"\n❌ TEST FAILED: Health index ({result['final_health_index']}) di bawah threshold tapi tidak ada auto-trigger")
    else:
        # Health tidak di bawah threshold
        print(f"\n⚠️ TEST SKIPPED: Health index ({result['final_health_index']}) tidak di bawah threshold {CRITICAL_THRESHOLD}")
        print(f"   Ini terjadi karena OEE Score dari database terlalu tinggi.")
        print(f"   RPN Score: {result['rpn_score']}%, OEE Score: {result['oee_score']}%")
        print(f"   Tips: Untuk test ini berhasil, OEE harus rendah (< 60%)")
    
    return result


def test_no_trigger_on_good_health():
    """
    Test 2: Verifikasi TIDAK ada pemicu saat health index >= CRITICAL_THRESHOLD
    """
    print("\n" + "="*80)
    print("TEST 2: No Trigger pada Good Health")
    print("="*80)
    
    health_service = HealthService()
    
    # Simulasi kondisi baik: RPN rendah (baik)
    rpn_value = 100  # RPN rendah = kondisi baik
    rpn_max = 1000
    
    print(f"\nInput Test:")
    print(f"  RPN Value: {rpn_value}")
    print(f"  RPN Max: {rpn_max}")
    print(f"  Expected RPN Score: {((1 - rpn_value/rpn_max) * 100):.2f}%")
    print(f"  Critical Threshold: {CRITICAL_THRESHOLD}")
    
    # Hitung health
    result = health_service.calculate_component_health(rpn_value, rpn_max)
    
    print(f"\nHasil Perhitungan:")
    print(f"  Final Health Index: {result['final_health_index']}")
    print(f"  Status: {result['status']}")
    
    # Verifikasi TIDAK ada auto-trigger
    if "auto_prediction" not in result:
        print(f"\n✅ TEST PASSED: Tidak ada auto-trigger (sesuai ekspektasi)")
    else:
        print(f"\n❌ TEST FAILED: Ada auto-trigger padahal health index ({result['final_health_index']}) di atas threshold")
    
    return result


def test_threshold_boundary():
    """
    Test 3: Test boundary condition (health index tepat di threshold)
    """
    print("\n" + "="*80)
    print("TEST 3: Boundary Condition Test")
    print("="*80)
    
    health_service = HealthService()
    
    # Coba berbagai nilai RPN untuk mencapai health index sekitar threshold
    # Note: OEE diambil dari database, jadi hasil bisa bervariasi
    test_cases = [
        (100, 1000, "Good condition (low RPN)"),
        (500, 1000, "Medium condition"),
        (900, 1000, "Poor condition (high RPN)"),
        (980, 1000, "Critical condition (very high RPN)"),
    ]
    
    for rpn_value, rpn_max, description in test_cases:
        print(f"\n{description}:")
        print(f"  RPN Value: {rpn_value}")
        
        result = health_service.calculate_component_health(rpn_value, rpn_max)
        health_index = result['final_health_index']
        has_trigger = "auto_prediction" in result
        
        print(f"  Health Index: {health_index}")
        print(f"  Auto-Trigger: {'YES ✅' if has_trigger else 'NO ❌'}")
        
        # Verifikasi logika
        if health_index < CRITICAL_THRESHOLD and has_trigger:
            print(f"  ✅ Correct: Health < {CRITICAL_THRESHOLD} dan trigger aktif")
        elif health_index >= CRITICAL_THRESHOLD and not has_trigger:
            print(f"  ✅ Correct: Health >= {CRITICAL_THRESHOLD} dan tidak ada trigger")
        else:
            print(f"  ❌ Error: Logika tidak konsisten!")


def test_force_critical_condition():
    """
    Test 4: Memaksa kondisi kritis dengan temporary threshold adjustment
    """
    print("\n" + "="*80)
    print("TEST 4: Force Critical Condition (Temporary Threshold)")
    print("="*80)
    
    print(f"\nStrategy: Sementara ubah CRITICAL_THRESHOLD ke nilai tinggi")
    print(f"          untuk memastikan auto-trigger terpicu\n")
    
    health_service = HealthService()
    
    # Test dengan RPN tinggi
    rpn_value = 900
    rpn_max = 1000
    
    print(f"Input Test:")
    print(f"  RPN Value: {rpn_value}")
    print(f"  RPN Max: {rpn_max}")
    print(f"  RPN Score: {((1 - rpn_value/rpn_max) * 100):.2f}%")
    
    result = health_service.calculate_component_health(rpn_value, rpn_max)
    
    print(f"\nHasil:")
    print(f"  Final Health Index: {result['final_health_index']}")
    print(f"  Current Threshold: {CRITICAL_THRESHOLD}")
    
    # Save original threshold
    original_threshold = CRITICAL_THRESHOLD
    
    # Temporarily increase threshold to force trigger
    import src.services.health_service as hs_module
    hs_module.CRITICAL_THRESHOLD = 80.0  # Set tinggi untuk force trigger
    
    print(f"\n🔧 Temporarily set threshold to: 80.0")
    
    # Test again with new threshold
    result2 = health_service.calculate_component_health(rpn_value, rpn_max)
    
    print(f"\nHasil dengan Threshold 80.0:")
    print(f"  Final Health Index: {result2['final_health_index']}")
    print(f"  Should Trigger: {result2['final_health_index'] < 80.0}")
    
    if "auto_prediction" in result2:
        print(f"\n✅ AUTO-TRIGGER DETECTED!")
        print(f"  Triggered: {result2['auto_prediction']['triggered']}")
        pred_result = result2['auto_prediction']['prediction_result']
        print(f"  Prediction Success: {pred_result.get('success')}")
        print(f"  Duration: {pred_result.get('prediction_formatted', 'N/A')}")
        print(f"\n✅ TEST PASSED: Auto-trigger berfungsi dengan baik!")
    else:
        if result2['final_health_index'] < 80.0:
            print(f"\n❌ TEST FAILED: Health < 80 tapi tidak ada trigger")
        else:
            print(f"\n⚠️ NOTE: Health masih >= 80 (OEE terlalu tinggi)")
    
    # Restore original threshold
    hs_module.CRITICAL_THRESHOLD = original_threshold
    print(f"\n🔧 Restored threshold to: {original_threshold}")


def test_prediction_service_availability():
    """
    Test 5: Verifikasi PredictionService dapat di-load dan digunakan
    """
    print("\n" + "="*80)
    print("TEST 5: Prediction Service Availability")
    print("="*80)
    
    try:
        prediction_service = PredictionService()
        
        print(f"\n✅ PredictionService berhasil di-instantiate")
        print(f"  Model Loaded: {prediction_service.model_loaded}")
        
        if prediction_service.model_loaded:
            # Test prediksi
            test_input = {
                "total_produksi": 5000,
                "produk_cacat": 150
            }
            
            print(f"\nTest Prediction:")
            print(f"  Input: {test_input}")
            
            result = prediction_service.predict_maintenance_duration(test_input)
            
            print(f"  Success: {result.get('success')}")
            print(f"  Duration: {result.get('prediction_formatted', 'N/A')}")
            
            if result.get('success'):
                print("\n✅ TEST PASSED: PredictionService siap digunakan")
            else:
                print(f"\n❌ TEST FAILED: Prediksi gagal - {result.get('message')}")
        else:
            print("\n⚠️ TEST WARNING: Model tidak ter-load")
            
    except Exception as e:
        print(f"\n❌ TEST FAILED: Error loading PredictionService - {str(e)}")


def run_all_tests():
    """
    Jalankan semua test
    """
    print("\n" + "="*80)
    print("AUTO-PREDICTION TRIGGER - TEST SUITE")
    print("="*80)
    print(f"Critical Threshold: {CRITICAL_THRESHOLD}")
    print("="*80)
    
    try:
        # Test 1: Auto-trigger pada critical health
        test_auto_trigger_on_critical_health()
        
        # Test 2: No trigger pada good health
        test_no_trigger_on_good_health()
        
        # Test 3: Boundary conditions
        test_threshold_boundary()
        
        # Test 4: Force critical condition
        test_force_critical_condition()
        
        # Test 5: PredictionService availability
        test_prediction_service_availability()
        
        print("\n" + "="*80)
        print("✅ ALL TESTS COMPLETED")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ TEST SUITE ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()

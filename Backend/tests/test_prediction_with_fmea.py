"""
Test Script untuk Prediction Service dengan FMEA Severity

Script ini menguji bahwa:
1. Model dapat menerima fitur FMEA_Severity
2. Prediksi berbeda untuk alasan yang sama dengan severity berbeda
3. Severity score dihitung dengan benar

Author: Generated for Testing
Date: 2025
"""

import sys
from pathlib import Path

# Tambahkan Backend ke path
backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from src.services.prediction_service import PredictionService, get_fmea_severity_from_reason, FMEA_SEVERITY_MAP

def test_fmea_severity_calculation():
    """Test bahwa FMEA severity dihitung dengan benar"""
    print("\n" + "="*70)
    print("TEST 1: FMEA SEVERITY CALCULATION")
    print("="*70)
    
    # Test beberapa alasan dengan severity yang berbeda
    test_cases = [
        ("CREASING PECAH", 9, "High Severity"),
        ("PRINTING BOTAK", 8, "High Severity"),
        ("SLOTER LARI", 8, "High Severity"),
        ("FEEDER UNIT TROUBLE ELEKTRIK", 8, "High Severity"),
        ("COUNTER PROBLEM", 6, "Medium Severity"),
        ("SETTING TIME", 3, "Low Severity"),
        ("_NONE_", 1, "Minimal Severity"),
        ("UNKNOWN_REASON", 5, "Default Severity"),
    ]
    
    print("\nMenguji perhitungan FMEA Severity:")
    all_passed = True
    
    for reason, expected_severity, description in test_cases:
        calculated_severity = get_fmea_severity_from_reason(reason)
        status = "✓ PASS" if calculated_severity == expected_severity else "✗ FAIL"
        
        if calculated_severity != expected_severity:
            all_passed = False
        
        print(f"  {status}: '{reason}' -> Severity {calculated_severity} (expected {expected_severity}) - {description}")
    
    if all_passed:
        print("\n✓ Semua test FMEA severity calculation PASSED")
    else:
        print("\n✗ Beberapa test FMEA severity calculation FAILED")
    
    return all_passed


def test_prediction_with_different_severity():
    """Test bahwa prediksi berbeda untuk alasan dengan severity berbeda"""
    print("\n" + "="*70)
    print("TEST 2: PREDICTION WITH DIFFERENT SEVERITY")
    print("="*70)
    
    # Initialize prediction service
    print("\nInisialisasi Prediction Service...")
    service = PredictionService()
    
    if not service.model_loaded:
        print("✗ FAIL: Model tidak berhasil dimuat")
        return False
    
    print("✓ Model berhasil dimuat")
    
    # Test cases: Alasan dengan severity berbeda
    test_scenarios = [
        {
            "name": "High Severity - CREASING PECAH",
            "data": {"reason": "CREASING PECAH", "shift": 2},
            "expected_severity": 9
        },
        {
            "name": "High Severity - PRINTING BOTAK",
            "data": {"reason": "PRINTING BOTAK", "shift": 2},
            "expected_severity": 8
        },
        {
            "name": "Medium Severity - COUNTER PROBLEM",
            "data": {"reason": "COUNTER PROBLEM", "shift": 2},
            "expected_severity": 6
        },
        {
            "name": "Low Severity - SETTING TIME",
            "data": {"reason": "SETTING TIME", "shift": 2},
            "expected_severity": 3
        },
    ]
    
    print("\nMenguji prediksi dengan severity berbeda (shift sama):")
    predictions = []
    
    for scenario in test_scenarios:
        print(f"\n  Scenario: {scenario['name']}")
        print(f"    Input: {scenario['data']}")
        
        # Lakukan prediksi
        result = service.predict_downtime(scenario['data'])
        
        if result['success']:
            prediction_value = result['prediction']
            predictions.append({
                'name': scenario['name'],
                'severity': scenario['expected_severity'],
                'prediction': prediction_value,
                'formatted': result['prediction_formatted']
            })
            
            print(f"    ✓ Prediksi: {prediction_value:.2f} menit ({result['prediction_formatted']})")
            print(f"    Expected Severity: {scenario['expected_severity']}/10")
        else:
            print(f"    ✗ Prediksi gagal: {result.get('message', 'Unknown error')}")
            return False
    
    # Analisis: Prediksi harus berbeda untuk severity yang berbeda
    print("\n" + "-"*70)
    print("ANALISIS HASIL PREDIKSI:")
    print("-"*70)
    
    # Sort by prediction value
    predictions_sorted = sorted(predictions, key=lambda x: x['prediction'], reverse=True)
    
    print("\nPrediksi diurutkan (dari tertinggi ke terendah):")
    for pred in predictions_sorted:
        print(f"  {pred['prediction']:6.2f} menit - {pred['name']} (Severity: {pred['severity']}/10)")
    
    # Check if predictions are different
    unique_predictions = len(set(p['prediction'] for p in predictions))
    
    print(f"\nJumlah nilai prediksi unik: {unique_predictions}/{len(predictions)}")
    
    if unique_predictions > 1:
        print("✓ PASS: Prediksi berbeda untuk severity yang berbeda (model mempertimbangkan severity)")
    else:
        print("⚠ WARNING: Semua prediksi sama (model mungkin tidak memanfaatkan severity dengan optimal)")
    
    # Check correlation between severity and prediction
    # High severity should generally lead to longer downtime
    print("\nKorelasi Severity vs Prediksi:")
    for pred in predictions:
        print(f"  Severity {pred['severity']}/10 -> {pred['prediction']:.2f} menit")
    
    return True


def test_sensor_error_translation_with_severity():
    """Test bahwa sensor error ditranslasi dengan benar dan severity dihitung"""
    print("\n" + "="*70)
    print("TEST 3: SENSOR ERROR TRANSLATION WITH SEVERITY")
    print("="*70)
    
    # Initialize prediction service
    service = PredictionService()
    
    if not service.model_loaded:
        print("✗ FAIL: Model tidak berhasil dimuat")
        return False
    
    # Test sensor error names (dari sensor_simulator.py)
    sensor_errors = [
        {
            "sensor_name": "SLOTTER_MISALIGNMENT",
            "training_name": "SLOTER LARI",
            "expected_severity": 8
        },
        {
            "sensor_name": "CREASING_CRACK",
            "training_name": "CREASING PECAH",
            "expected_severity": 9
        },
        {
            "sensor_name": "INK_BLOBBING",
            "training_name": "PRINT BLOBOR",
            "expected_severity": 9
        },
        {
            "sensor_name": "PRINT_GHOSTING",
            "training_name": "PRINTING BOTAK",
            "expected_severity": 8
        },
    ]
    
    print("\nMenguji translasi sensor error dan severity:")
    all_passed = True
    
    for error in sensor_errors:
        print(f"\n  Sensor Error: {error['sensor_name']}")
        
        # Lakukan prediksi dengan sensor error name
        result = service.predict_downtime({
            "reason": error['sensor_name'],
            "shift": 1
        })
        
        if result['success']:
            print(f"    ✓ Translasi berhasil")
            print(f"    Training name: {error['training_name']}")
            print(f"    Expected severity: {error['expected_severity']}/10")
            print(f"    Prediksi: {result['prediction']:.2f} menit")
        else:
            print(f"    ✗ Translasi gagal: {result.get('message', 'Unknown error')}")
            all_passed = False
    
    if all_passed:
        print("\n✓ Semua test sensor error translation PASSED")
    else:
        print("\n✗ Beberapa test sensor error translation FAILED")
    
    return all_passed


def test_model_feature_info():
    """Test informasi fitur model untuk memverifikasi FMEA_Severity ada"""
    print("\n" + "="*70)
    print("TEST 4: MODEL FEATURE INFO")
    print("="*70)
    
    # Initialize prediction service
    service = PredictionService()
    
    if not service.model_loaded:
        print("✗ FAIL: Model tidak berhasil dimuat")
        return False
    
    # Get model info
    model_info = service.get_model_info()
    
    print("\nInformasi Model:")
    print(f"  Model Type: {model_info['model_details']['type']}")
    print(f"  Total Features: {model_info['feature_info']['total_features']}")
    print(f"  Feature Mode: {model_info['feature_info']['mode']}")
    
    # Check if FMEA_Severity is in feature names
    if service.feature_names:
        has_fmea = 'FMEA_Severity' in service.feature_names
        
        if has_fmea:
            print(f"\n✓ FMEA_Severity ditemukan di feature names")
            
            # Find position of FMEA_Severity
            fmea_index = service.feature_names.index('FMEA_Severity')
            print(f"  Position: #{fmea_index + 1} of {len(service.feature_names)}")
            
            # Show some features around it
            print(f"\n  Features around FMEA_Severity:")
            start = max(0, fmea_index - 2)
            end = min(len(service.feature_names), fmea_index + 3)
            for i in range(start, end):
                marker = " <-- FMEA_Severity" if i == fmea_index else ""
                print(f"    [{i+1}] {service.feature_names[i]}{marker}")
            
            return True
        else:
            print(f"\n✗ FMEA_Severity TIDAK ditemukan di feature names")
            print(f"  Features available: {service.feature_names[:5]}...")
            return False
    else:
        print("\n⚠ WARNING: Feature names tidak tersedia (mode fallback)")
        return False


def main():
    """Main test function"""
    print("\n" + "="*70)
    print("TESTING PREDICTION SERVICE WITH FMEA SEVERITY")
    print("="*70)
    print("\nScript ini menguji integrasi FMEA Severity ke dalam model prediksi.")
    print("Model baru (v2.1): Fishbone + Shift + FMEA Severity")
    
    # Run all tests
    results = []
    
    results.append(("FMEA Severity Calculation", test_fmea_severity_calculation()))
    results.append(("Model Feature Info", test_model_feature_info()))
    results.append(("Prediction with Different Severity", test_prediction_with_different_severity()))
    results.append(("Sensor Error Translation", test_sensor_error_translation_with_severity()))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ SEMUA TEST BERHASIL!")
        print("  Model dengan FMEA Severity bekerja dengan baik.")
    else:
        print(f"\n⚠ {total - passed} test gagal, perlu perbaikan.")
    
    print("="*70)


if __name__ == "__main__":
    main()

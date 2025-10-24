"""
test_model_with_shift.py
Test model baru yang menggunakan fitur Shift
"""

import joblib
import pandas as pd
from pathlib import Path

# Load model dan feature names
MODEL_PATH = Path(__file__).parent / "model.pkl"
FEATURE_NAMES_PATH = Path(__file__).parent / "feature_names.pkl"

print("="*80)
print("  TEST MODEL DENGAN FITUR SHIFT")
print("="*80)

# Load artifacts
model = joblib.load(MODEL_PATH)
feature_names = joblib.load(FEATURE_NAMES_PATH)

print(f"\n✓ Model loaded: {type(model).__name__}")
print(f"✓ Total features: {len(feature_names)}")

# Cek fitur Shift
shift_features = [f for f in feature_names if f.startswith('Shift_')]
print(f"\n📊 Shift features ditemukan ({len(shift_features)}):")
for sf in shift_features:
    print(f"   - {sf}")

# Test cases dengan berbagai kombinasi reason + shift
test_cases = [
    {"reason": "SLOTER LARI", "shift": 1, "desc": "Slotter misalignment - Shift Pagi"},
    {"reason": "SLOTER LARI", "shift": 2, "desc": "Slotter misalignment - Shift Siang"},
    {"reason": "SLOTER LARI", "shift": 3, "desc": "Slotter misalignment - Shift Malam"},
    {"reason": "FEEDER UNIT TROUBLE ELEKTRIK", "shift": 1, "desc": "Feeder elektrik - Shift Pagi"},
    {"reason": "FEEDER UNIT TROUBLE ELEKTRIK", "shift": 2, "desc": "Feeder elektrik - Shift Siang"},
    {"reason": "FEEDER UNIT TROUBLE ELEKTRIK", "shift": 3, "desc": "Feeder elektrik - Shift Malam"},
    {"reason": "PRINTING BOTAK", "shift": 1, "desc": "Printing botak - Shift Pagi"},
    {"reason": "PRINTING BOTAK", "shift": 2, "desc": "Printing botak - Shift Siang"},
    {"reason": "CREASING PECAH", "shift": 2, "desc": "Creasing pecah - Shift Siang"},
]

print("\n" + "="*80)
print("  PREDICTION RESULTS")
print("="*80)

print(f"\n{'Description':<45} {'Shift':<8} {'Predicted (min)':<18}")
print("-" * 80)

for test in test_cases:
    # Prepare feature array
    feature_array = pd.DataFrame(0, index=[0], columns=feature_names)
    
    # Set reason
    reason = test['reason']
    scrab_key = f"Scrab Description_{reason}"
    break_key = f"Break Time Description_{reason}"
    
    if scrab_key in feature_names:
        feature_array[scrab_key] = 1
    elif break_key in feature_names:
        feature_array[break_key] = 1
    
    # Set shift
    shift = test['shift']
    shift_key = f"Shift_{float(shift):.1f}"  # Format: Shift_1.0, Shift_2.0
    
    if shift_key in feature_names:
        feature_array[shift_key] = 1
    
    # Predict
    try:
        prediction = model.predict(feature_array)[0]
        print(f"{test['desc']:<45} Shift {shift:<6} {prediction:>8.1f} menit")
    except Exception as e:
        print(f"{test['desc']:<45} Shift {shift:<6} ERROR: {e}")

print("\n" + "="*80)
print("✓ Test selesai!")
print("="*80)

print("\n💡 Analisis:")
print("   • Jika prediksi BERBEDA untuk shift yang berbeda → Shift berpengaruh ✅")
print("   • Jika prediksi SAMA → Shift tidak berpengaruh (perlu lebih banyak data) ⚠️")

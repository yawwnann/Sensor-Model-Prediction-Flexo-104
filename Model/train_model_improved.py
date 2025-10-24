"""
SOLUSI: Fix R² negatif dengan:
1. Filter outlier ekstrem (>1000 menit)
2. Log transform target variable
3. Hyperparameter tuning
"""
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import MultiLabelBinarizer
import joblib
import warnings
warnings.filterwarnings('ignore')

# Import functions from train_model.py
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
from train_model import (
    load_and_concat_csv, 
    load_repair_history,
    merge_production_with_repairs,
    normalize_text,
    similarity_score
)

print("="*70)
print("FIX MODEL: FILTER OUTLIER + LOG TRANSFORM + TUNING")
print("="*70)

def preprocess_with_outlier_filter(df: pd.DataFrame, max_duration: int = 1000) -> pd.DataFrame:
    """
    Enhanced preprocessing dengan filter outlier
    
    Args:
        df: DataFrame hasil merge
        max_duration: Maximum realistic downtime duration (default: 1000 menit = 16.7 jam)
    """
    print(f"\n[PREPROCESSING WITH OUTLIER FILTER]")
    print(f"="*70)
    
    # Filter C_FL104
    df = df[df['Work Center'] == 'C_FL104'].copy()
    print(f"✓ Data C_FL104: {len(df)} baris")
    
    # Filter kontaminasi (summary rows)
    mask_valid = (
        df['Scrab Description'].notna() |
        df['Break Time Description'].notna()
    )
    df = df[mask_valid].copy()
    print(f"✓ Setelah filter kontaminasi: {len(df)} baris")
    
    # Filter operational downtime
    operational_keywords = ['GANTI ORDER', 'GANTI WO', 'MAINTENANCE', 'SETUP', 'TRIAL', 'TUNGGU']
    df['Is_Operational'] = df.apply(
        lambda row: any(keyword in str(row.get('Scrab Description', '')).upper() for keyword in operational_keywords) or
                    any(keyword in str(row.get('Break Time Description', '')).upper() for keyword in operational_keywords),
        axis=1
    )
    df = df[~df['Is_Operational']].copy()
    print(f"✓ Setelah filter operational: {len(df)} baris")
    
    # ⭐ FILTER OUTLIER EKSTREM
    print(f"\n⭐ FILTER OUTLIER EKSTREM (>{max_duration} menit)")
    print(f"-"*70)
    before_filter = len(df)
    outliers = df[df['Stop Time'] > max_duration]
    print(f"  Data sebelum filter: {before_filter} baris")
    print(f"  Outlier terdeteksi: {len(outliers)} baris ({len(outliers)/before_filter*100:.1f}%)")
    print(f"  Range outlier: {outliers['Stop Time'].min():.0f} - {outliers['Stop Time'].max():.0f} menit")
    
    df = df[df['Stop Time'] <= max_duration].copy()
    print(f"  ✓ Data setelah filter: {len(df)} baris")
    
    # Statistics after filter
    print(f"\n📊 Statistik Target Variable (setelah filter):")
    print(f"  Mean: {df['Stop Time'].mean():.2f} menit")
    print(f"  Median: {df['Stop Time'].median():.2f} menit")
    print(f"  Std: {df['Stop Time'].std():.2f} menit")
    print(f"  CV: {(df['Stop Time'].std()/df['Stop Time'].mean())*100:.1f}%")
    print(f"  Min: {df['Stop Time'].min():.0f} menit")
    print(f"  Max: {df['Stop Time'].max():.0f} menit")
    
    # ⭐ LOG TRANSFORM TARGET
    print(f"\n⭐ LOG TRANSFORM TARGET VARIABLE")
    print(f"-"*70)
    # Add small constant to avoid log(0)
    df['Stop_Time_Original'] = df['Stop Time'].copy()
    df['Stop Time'] = np.log1p(df['Stop Time'])  # log(1 + x)
    
    print(f"  ✓ Target transformed: log1p(Stop Time)")
    print(f"  Original range: {df['Stop_Time_Original'].min():.0f} - {df['Stop_Time_Original'].max():.0f} menit")
    print(f"  Transformed range: {df['Stop Time'].min():.2f} - {df['Stop Time'].max():.2f}")
    
    return df

def train_model_enhanced(df: pd.DataFrame) -> tuple:
    """
    Train model dengan hyperparameter tuning
    """
    print(f"\n[FEATURE ENGINEERING]")
    print(f"="*70)
    
    # FMEA Severity mapping
    FMEA_mapping = {
        'PRINTING BOTAK': 9, 'PRINTING DOUBLE': 8, 'PRINTING BLUR': 7,
        'CREASING MIRING': 8, 'CREASING PECAH': 9, 'CREASING LARI': 7,
        'SLOTTER PECAH': 9, 'SLOTTER LARI': 6, 'SLOTER LARI': 6,
        'DIECUT TIDAK PUTUS': 8, 'DIECUT PECAH': 9, 'FEEDER TROUBLE': 7,
        'FEEDER ELEKTRIK': 8, 'FEEDER MEKANIK': 7, 'GANTI ORDER': 1,
        'MAINTENANCE': 5, 'SETUP': 1
    }
    
    def calculate_severity(row):
        scrab = str(row.get('Scrab Description', '')).upper()
        breaktime = str(row.get('Break Time Description', '')).upper()
        for key, severity in FMEA_mapping.items():
            if key in scrab or key in breaktime:
                return severity
        return 5
    
    df['FMEA_Severity'] = df.apply(calculate_severity, axis=1)
    print(f"✓ FMEA Severity calculated (range: {df['FMEA_Severity'].min()}-{df['FMEA_Severity'].max()})")
    
    # Encode TEKNISI
    mlb = MultiLabelBinarizer()
    teknisi_encoded = mlb.fit_transform(df['TEKNISI_LIST'])
    teknisi_cols = [f'TEKNISI_{name}' for name in mlb.classes_]
    df_teknisi = pd.DataFrame(teknisi_encoded, columns=teknisi_cols, index=df.index)
    df = pd.concat([df, df_teknisi], axis=1)
    print(f"✓ Teknisi encoded: {len(teknisi_cols)} features")
    
    # Encode ACTION_PLAN (top 20)
    action_counts = df['ACTION_PLAN_CLEANED'].value_counts()
    top_actions = action_counts.head(20).index.tolist()
    
    for action in top_actions:
        if action:
            col_name = f"ACTION_{action[:40]}"
            df[col_name] = (df['ACTION_PLAN_CLEANED'] == action).astype(int)
    
    action_cols = [col for col in df.columns if col.startswith('ACTION_')]
    print(f"✓ Action plan encoded: {len(action_cols)} features")
    
    # One-hot encode categorical
    df_encoded = pd.get_dummies(
        df,
        columns=['Scrab Description', 'Break Time Description', 'Shift'],
        drop_first=False,
        dtype=int
    )
    
    # Prepare features
    features_to_drop = [
        'Stop Time', 'Stop_Time_Original', 'Date', 'Time', 'Work Center',
        'TEKNISI_LIST', 'ACTION_PLAN_CLEANED', 'ISSUE_NORMALIZED',
        'Is_Operational', 'HAS_SPARE_PART', 'ISSUE', 'Scrab_Duration',
        'Break_Duration', 'ORIGINAL_IDX', 'SIMILARITY_SCORE'
    ]
    
    # Filter out any remaining non-numeric columns
    feature_cols = []
    for col in df_encoded.columns:
        if col not in features_to_drop:
            # Check if column is numeric or boolean
            if df_encoded[col].dtype in ['int64', 'float64', 'bool', 'int32', 'float32']:
                feature_cols.append(col)
            elif col.startswith(('TEKNISI_', 'ACTION_', 'Scrab Description_', 'Break Time Description_', 'Shift_')):
                feature_cols.append(col)
    
    # Add HAS_SPARE_PART back
    if 'HAS_SPARE_PART' in df_encoded.columns:
        feature_cols.insert(0, 'HAS_SPARE_PART')
    
    X = df_encoded[feature_cols].fillna(0)
    y = df_encoded['Stop Time']
    
    print(f"\n✓ Total features: {len(feature_cols)}")
    print(f"  - Teknisi: {len(teknisi_cols)}")
    print(f"  - Action Plan: {len(action_cols)}")
    print(f"  - Other: {len(feature_cols) - len(teknisi_cols) - len(action_cols)}")
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\n[TRAINING WITH ENHANCED HYPERPARAMETERS]")
    print(f"="*70)
    print(f"Training size: {len(X_train)} | Test size: {len(X_test)}")
    
    # ⭐ TUNED HYPERPARAMETERS
    model = RandomForestRegressor(
        n_estimators=200,        # ↑ from 100
        max_depth=15,            # ⭐ NEW: prevent overfitting
        min_samples_split=20,    # ⭐ NEW: reduce overfitting
        min_samples_leaf=10,     # ⭐ NEW: smoother predictions
        max_features='sqrt',     # ⭐ NEW: reduce correlation
        random_state=42,
        n_jobs=-1,
        verbose=0
    )
    
    print(f"\nHyperparameters:")
    print(f"  n_estimators: 200")
    print(f"  max_depth: 15")
    print(f"  min_samples_split: 20")
    print(f"  min_samples_leaf: 10")
    print(f"  max_features: sqrt")
    
    model.fit(X_train, y_train)
    
    # Predictions (in log space)
    y_pred_log = model.predict(X_test)
    
    # ⭐ INVERSE TRANSFORM
    y_test_original = np.expm1(y_test)  # exp(x) - 1
    y_pred_original = np.expm1(y_pred_log)
    
    # Metrics in ORIGINAL space
    mae = mean_absolute_error(y_test_original, y_pred_original)
    rmse = np.sqrt(mean_squared_error(y_test_original, y_pred_original))
    r2 = r2_score(y_test_original, y_pred_original)
    
    print(f"\n{'='*70}")
    print(f"HASIL EVALUASI (ORIGINAL SPACE - MENIT)")
    print(f"{'='*70}")
    print(f"MAE:  {mae:.2f} menit")
    print(f"RMSE: {rmse:.2f} menit")
    print(f"R²:   {r2:.4f}")
    
    if r2 > 0:
        print(f"\n✅ R² POSITIF! Model lebih baik dari baseline!")
    else:
        print(f"\n⚠️ R² masih negatif, perlu tuning lebih lanjut")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': feature_cols,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\nTOP 10 FEATURE IMPORTANCE:")
    print(f"-"*70)
    for i, row in feature_importance.head(10).iterrows():
        print(f"  {row['importance']:.4f} - {row['feature']}")
    
    return model, feature_cols, mae, rmse, r2, feature_importance

# Main execution
def main():
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir.parent / "Data Flexo CSV"
    repair_file = base_dir / "RIWAYAT_PERBAIKAN_REALISTIC.csv"
    
    # Load data
    print(f"\n[STEP 1] Load production data...")
    df_prod, _ = load_and_concat_csv(data_dir)
    
    print(f"\n[STEP 2] Load repair history...")
    df_repair = load_repair_history(repair_file)
    
    print(f"\n[STEP 3] Merge data...")
    df_merged = merge_production_with_repairs(df_prod, df_repair)
    
    print(f"\n[STEP 4] Preprocess with outlier filter...")
    df_processed = preprocess_with_outlier_filter(df_merged, max_duration=1000)
    
    if len(df_processed) < 100:
        print(f"\n❌ ERROR: Insufficient data after filtering ({len(df_processed)} rows)")
        return
    
    print(f"\n[STEP 5] Train model...")
    model, feature_cols, mae, rmse, r2, importance = train_model_enhanced(df_processed)
    
    # Save model
    output_file = base_dir / "model_improved.pkl"
    joblib.dump(model, output_file)
    joblib.dump(feature_cols, base_dir / "feature_names_improved.pkl")
    importance.to_csv(base_dir / "feature_importance_improved.csv", index=False)
    
    print(f"\n{'='*70}")
    print(f"✅ MODEL IMPROVED BERHASIL DISIMPAN!")
    print(f"{'='*70}")
    print(f"File: {output_file}")
    print(f"\nMetrics:")
    print(f"  MAE:  {mae:.2f} menit")
    print(f"  RMSE: {rmse:.2f} menit")
    print(f"  R²:   {r2:.4f}")
    print(f"{'='*70}\n")

if __name__ == "__main__":
    main()

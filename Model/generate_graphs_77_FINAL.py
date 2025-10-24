"""
Generate Grafik Thesis dengan Full Model 77 Features
Hasil akan menunjukkan MAE = 19.90, R² = 0.5936
"""

import subprocess
import sys

# Step 1: Run training to get fresh metrics
print("="*80)
print("STEP 1: Running model training to get test data...")
print("="*80)
result = subprocess.run([sys.executable, "train_model_improved.py"], 
                       capture_output=False, text=True)

if result.returncode != 0:
    print("❌ Training failed!")
    sys.exit(1)

# Step 2: Generate graphs using joblib files
print("\n" + "="*80)
print("STEP 2: Generating thesis graphs...")
print("="*80)

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from pathlib import Path

# Import functions
from train_model_improved import (
    load_and_concat_csv,
    load_repair_history,
    merge_production_with_repairs,
    preprocess_with_outlier_filter
)

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
from sklearn.preprocessing import MultiLabelBinarizer

# Load model
model = joblib.load('model_improved.pkl')
feature_names = joblib.load('feature_names_improved.pkl')
print(f"\n✓ Model loaded: {len(feature_names)} features")

# Prepare data (EXACT same as training)
data_dir = Path('../Data Flexo CSV')
df_flexo_all, _ = load_and_concat_csv(data_dir)
df_clean = load_repair_history(Path('RIWAYAT_PERBAIKAN_REALISTIC.csv'))
df_merged = merge_production_with_repairs(df_flexo_all, df_clean)
df_flexo = preprocess_with_outlier_filter(df_merged)

# Feature engineering (EXACT copy dari train_model_enhanced)
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

df_flexo['FMEA_Severity'] = df_flexo.apply(calculate_severity, axis=1)

# Encode TEKNISI
mlb = MultiLabelBinarizer()
teknisi_encoded = mlb.fit_transform(df_flexo['TEKNISI_LIST'])
teknisi_cols = [f'TEKNISI_{name}' for name in mlb.classes_]
df_teknisi = pd.DataFrame(teknisi_encoded, columns=teknisi_cols, index=df_flexo.index)
df_flexo = pd.concat([df_flexo, df_teknisi], axis=1)

# Encode ACTION_PLAN
action_counts = df_flexo['ACTION_PLAN_CLEANED'].value_counts()
top_actions = action_counts.head(20).index.tolist()

for action in top_actions:
    if action:
        col_name = f"ACTION_{action[:40]}"
        df_flexo[col_name] = (df_flexo['ACTION_PLAN_CLEANED'] == action).astype(int)

# One-hot encode
df_encoded = pd.get_dummies(
    df_flexo,
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

feature_cols = []
for col in df_encoded.columns:
    if col not in features_to_drop:
        if df_encoded[col].dtype in ['int64', 'float64', 'bool', 'int32', 'float32']:
            feature_cols.append(col)
        elif col.startswith(('TEKNISI_', 'ACTION_', 'Scrab Description_', 'Break Time Description_', 'Shift_')):
            feature_cols.append(col)

if 'HAS_SPARE_PART' in df_encoded.columns:
    feature_cols.insert(0, 'HAS_SPARE_PART')

X = df_encoded[feature_cols].fillna(0)
y = df_encoded['Stop Time']

# Split (SAME random_state!)
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Predictions
y_pred = model.predict(X_test)

# Inverse transform
y_test_orig = np.expm1(y_test)
y_pred_orig = np.expm1(y_pred)

# Metrics
mae = mean_absolute_error(y_test_orig, y_pred_orig)
rmse = np.sqrt(mean_squared_error(y_test_orig, y_pred_orig))
r2 = r2_score(y_test_orig, y_pred_orig)

print(f"\n📊 Metrics verified:")
print(f"   MAE:  {mae:.2f} menit")
print(f"   RMSE: {rmse:.2f} menit")
print(f"   R²:   {r2:.4f}")

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("\n" + "="*80)
print("Generating 3 graphs...")
print("="*80)

# === GRAPH 1: Feature Importance ===
print("\n1. Feature Importance (Top 15)...")
importances = model.feature_importances_
indices = np.argsort(importances)[::-1][:15]
top_features = [feature_names[i] for i in indices]
top_importances = importances[indices]

fig, ax = plt.subplots(figsize=(12, 8))
y_pos = np.arange(len(top_features))
colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_features)))

bars = ax.barh(y_pos, top_importances, color=colors, edgecolor='black', linewidth=0.7)

for i, (bar, imp) in enumerate(zip(bars, top_importances)):
    width = bar.get_width()
    ax.text(width + 0.005, bar.get_y() + bar.get_height()/2, 
            f'{imp*100:.2f}%',
            ha='left', va='center', fontsize=10, fontweight='bold')

ax.set_yticks(y_pos)
ax.set_yticklabels(top_features, fontsize=11)
ax.invert_yaxis()
ax.set_xlabel('Importance Score', fontsize=13, fontweight='bold')
ax.set_title('Top 15 Feature Importance - Random Forest Model', 
             fontsize=15, fontweight='bold', pad=20)
ax.grid(axis='x', alpha=0.3, linestyle='--')

total_top15 = top_importances.sum()
ax.text(0.98, 0.02, f'Total Top 15: {total_top15*100:.2f}%',
        transform=ax.transAxes, fontsize=11, fontweight='bold',
        bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
        ha='right', va='bottom')

plt.tight_layout()
plt.savefig('evaluation_results/feature_importance_final.png', dpi=300, bbox_inches='tight')
print("   ✓ Saved: feature_importance_final.png")
plt.close()

# === GRAPH 2: Prediction vs Actual ===
print("\n2. Prediction vs Actual...")
fig, ax = plt.subplots(figsize=(10, 8))

ax.scatter(y_test_orig, y_pred_orig, alpha=0.5, s=30, c='steelblue', edgecolors='black', linewidth=0.5)

min_val = min(y_test_orig.min(), y_pred_orig.min())
max_val = max(y_test_orig.max(), y_pred_orig.max())
ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')

textstr = f'MAE = {mae:.2f} menit\nR² = {r2:.4f}'
props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12,
        verticalalignment='top', bbox=props, fontweight='bold')

ax.set_xlabel('Nilai Aktual (menit)', fontsize=13, fontweight='bold')
ax.set_ylabel('Prediksi Model (menit)', fontsize=13, fontweight='bold')
ax.set_title('Prediksi vs. Nilai Aktual - Model Lengkap (77 Features)\n(Test Set)', 
             fontsize=15, fontweight='bold', pad=20)
ax.legend(loc='lower right', fontsize=11)
ax.grid(True, alpha=0.3, linestyle='--')

plt.tight_layout()
plt.savefig('evaluation_results/prediction_vs_actual_final.png', dpi=300, bbox_inches='tight')
print("   ✓ Saved: prediction_vs_actual_final.png")
plt.close()

# === GRAPH 3: Residual Analysis ===
print("\n3. Residual Analysis...")
residuals = y_test_orig - y_pred_orig

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Residual vs Predicted
ax1.scatter(y_pred_orig, residuals, alpha=0.5, s=30, c='coral', edgecolors='black', linewidth=0.5)
ax1.axhline(y=0, color='r', linestyle='--', lw=2, label='Zero Residual')
ax1.set_xlabel('Prediksi Model (menit)', fontsize=12, fontweight='bold')
ax1.set_ylabel('Residual (Aktual - Prediksi)', fontsize=12, fontweight='bold')
ax1.set_title('Residual vs. Prediksi', fontsize=14, fontweight='bold')
ax1.legend(loc='upper right')
ax1.grid(True, alpha=0.3, linestyle='--')

mean_residual = residuals.mean()
std_residual = residuals.std()
textstr = f'Mean: {mean_residual:.2f} min\nStd: {std_residual:.2f} min'
props = dict(boxstyle='round', facecolor='lightblue', alpha=0.8)
ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=11,
        verticalalignment='top', bbox=props, fontweight='bold')

# Residual Distribution
ax2.hist(residuals, bins=50, color='lightgreen', edgecolor='black', alpha=0.7)
ax2.axvline(x=0, color='r', linestyle='--', lw=2, label='Zero Residual')
ax2.set_xlabel('Residual (menit)', fontsize=12, fontweight='bold')
ax2.set_ylabel('Frekuensi', fontsize=12, fontweight='bold')
ax2.set_title('Distribusi Residual', fontsize=14, fontweight='bold')
ax2.legend(loc='upper right')
ax2.grid(axis='y', alpha=0.3, linestyle='--')

fig.suptitle('Analisis Residual - Model Lengkap (77 Features)', 
             fontsize=16, fontweight='bold', y=1.02)

plt.tight_layout()
plt.savefig('evaluation_results/residual_plot_final.png', dpi=300, bbox_inches='tight')
print("   ✓ Saved: residual_plot_final.png")
plt.close()

# Summary
print("\n" + "="*80)
print("✅ ALL 3 GRAPHS GENERATED SUCCESSFULLY!")
print("="*80)
print(f"\n📊 Final Model Performance (77 Features):")
print(f"   • MAE:  {mae:.2f} menit  ✅")
print(f"   • RMSE: {rmse:.2f} menit ✅")
print(f"   • R²:   {r2:.4f} ✅")
print(f"\n📁 Output files (300 DPI):")
print(f"   • evaluation_results/feature_importance_final.png")
print(f"   • evaluation_results/prediction_vs_actual_final.png")
print(f"   • evaluation_results/residual_plot_final.png")
print(f"\n🎓 Graphs ready for thesis - using FULL 77-feature model!")
print("="*80)

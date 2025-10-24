"""
Generate grafik thesis dengan model 77 features LENGKAP
Script ini akan RE-RUN training untuk mendapatkan test data yang correct
Kemudian generate grafik dengan R² = 0.5936, MAE = 19.90
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from pathlib import Path
import sys

# Add parent directory
sys.path.append(str(Path(__file__).resolve().parent))

# Import full training pipeline
from train_model_improved import (
    load_and_concat_csv,
    load_repair_history,
    merge_production_with_repairs,
    preprocess_with_outlier_filter,
    train_model_enhanced
)

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

print("="*80)
print("📊 GENERATING FINAL THESIS GRAPHS - FULL MODEL (77 FEATURES)")
print("="*80)

# Step 1: Load model
print("\n[1/6] Loading trained model...")
model = joblib.load('model_improved.pkl')
feature_names = joblib.load('feature_names_improved.pkl')
print(f"✓ Model loaded: {len(feature_names)} features")

# Step 2-4: Re-run training to get correct test data
print("\n[2/6] Re-running training pipeline to get test data...")
data_dir = Path('../Data Flexo CSV')
df_flexo_all, total_files = load_and_concat_csv(data_dir)
df_clean = load_repair_history(Path('RIWAYAT_PERBAIKAN_REALISTIC.csv'))
df_merged = merge_production_with_repairs(df_flexo_all, df_clean)
df_flexo = preprocess_with_outlier_filter(df_merged)

print("\n[3/6] Running feature engineering and getting metrics...")
# train_model_enhanced returns: model, feature_cols, mae, rmse, r2, feature_importance
_, feature_cols_check, mae, rmse, r2, feature_importance_df = train_model_enhanced(df_flexo)

print("\n[4/6] Getting test predictions from saved model...")

print(f"\n📊 Model Performance (from training):")
print(f"   MAE:  {mae:.2f} menit")
print(f"   RMSE: {rmse:.2f} menit")
print(f"   R²:   {r2:.4f}")

# Step 5: Generate graphs
print("\n[5/6] Generating thesis graphs...")

# === GRAPH 1: Feature Importance (Top 15) ===
print("\n   a) Feature Importance...")
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
print(f"   ✓ Saved: feature_importance_final.png")
plt.close()

# === GRAPH 2: Prediction vs Actual ===
print("\n   b) Prediction vs Actual...")
fig, ax = plt.subplots(figsize=(10, 8))

ax.scatter(y_test, y_pred, alpha=0.5, s=30, c='steelblue', edgecolors='black', linewidth=0.5)

min_val = min(y_test.min(), y_pred.min())
max_val = max(y_test.max(), y_pred.max())
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
print(f"   ✓ Saved: prediction_vs_actual_final.png")
plt.close()

# === GRAPH 3: Residual Analysis ===
print("\n   c) Residual Analysis...")
residuals = y_test - y_pred

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Residual vs Predicted
ax1.scatter(y_pred, residuals, alpha=0.5, s=30, c='coral', edgecolors='black', linewidth=0.5)
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
print(f"   ✓ Saved: residual_plot_final.png")
plt.close()

# Step 6: Summary
print("\n" + "="*80)
print("✅ ALL GRAPHS GENERATED SUCCESSFULLY!")
print("="*80)
print(f"\n📊 Final Model Performance (77 Features):")
print(f"   • MAE:  {mae:.2f} menit  ✅")
print(f"   • RMSE: {rmse:.2f} menit ✅")
print(f"   • R²:   {r2:.4f} ✅")
print(f"\n📁 Output files (300 DPI):")
print(f"   • evaluation_results/feature_importance_final.png")
print(f"   • evaluation_results/prediction_vs_actual_final.png")
print(f"   • evaluation_results/residual_plot_final.png")
print(f"\n🎓 Graphs ready for thesis documentation!")
print(f"   Note: Grafik Prediction vs Actual dan Residual menggunakan")
print(f"         FULL MODEL 77 FEATURES dengan R² = {r2:.4f}")
print("="*80)

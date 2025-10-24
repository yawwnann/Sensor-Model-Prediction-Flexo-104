"""
Script untuk generate grafik thesis dengan model 77 features LENGKAP
Fix: Prediction vs Actual dan Residual menggunakan full model (R² = 0.5936, MAE = 19.90)
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Import dari train_model_improved
from train_model_improved import (
    preprocess_with_outlier_filter, 
    train_model_enhanced,
    load_and_concat_csv,
    load_repair_history,
    merge_production_with_repairs
)

# Set style
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

def plot_feature_importance_top15(model, feature_names, output_path='evaluation_results/feature_importance_final.png'):
    """Plot top 15 feature importance (horizontal bar)"""
    
    importances = model.feature_importances_
    indices = np.argsort(importances)[::-1]
    
    # Ambil top 15 saja
    top_n = 15
    top_indices = indices[:top_n]
    top_features = [feature_names[i] for i in top_indices]
    top_importances = importances[top_indices]
    
    # Create figure
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Horizontal bar chart
    y_pos = np.arange(len(top_features))
    colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(top_features)))
    
    bars = ax.barh(y_pos, top_importances, color=colors, edgecolor='black', linewidth=0.7)
    
    # Add value labels
    for i, (bar, imp) in enumerate(zip(bars, top_importances)):
        width = bar.get_width()
        ax.text(width + 0.005, bar.get_y() + bar.get_height()/2, 
                f'{imp*100:.2f}%',
                ha='left', va='center', fontsize=10, fontweight='bold')
    
    # Styling
    ax.set_yticks(y_pos)
    ax.set_yticklabels(top_features, fontsize=11)
    ax.invert_yaxis()
    ax.set_xlabel('Importance Score', fontsize=13, fontweight='bold')
    ax.set_title('Top 15 Feature Importance - Random Forest Model', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.grid(axis='x', alpha=0.3, linestyle='--')
    
    # Add total importance text
    total_top15 = top_importances.sum()
    ax.text(0.98, 0.02, f'Total Top 15: {total_top15*100:.2f}%',
            transform=ax.transAxes,
            fontsize=11, fontweight='bold',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5),
            ha='right', va='bottom')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Feature importance plot saved: {output_path}")
    print(f"   Top feature: {top_features[0]} ({top_importances[0]*100:.2f}%)")
    plt.close()


def plot_prediction_vs_actual_full_model(model, X_test, y_test, output_path='evaluation_results/prediction_vs_actual_final.png'):
    """
    Plot Prediction vs Actual menggunakan FULL MODEL (77 features)
    Ini akan menghasilkan R² = 0.5936 dan MAE = 19.90
    """
    from sklearn.metrics import mean_absolute_error, r2_score
    
    # Prediksi menggunakan FULL MODEL
    y_pred = model.predict(X_test)
    
    # Calculate metrics
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Scatter plot
    scatter = ax.scatter(y_test, y_pred, alpha=0.5, s=30, c='steelblue', edgecolors='black', linewidth=0.5)
    
    # Perfect prediction line
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 'r--', lw=2, label='Perfect Prediction')
    
    # Add metrics text box
    textstr = f'MAE = {mae:.2f} menit\nR² = {r2:.4f}'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=12,
            verticalalignment='top', bbox=props, fontweight='bold')
    
    # Styling
    ax.set_xlabel('Nilai Aktual (menit)', fontsize=13, fontweight='bold')
    ax.set_ylabel('Prediksi Model (menit)', fontsize=13, fontweight='bold')
    ax.set_title('Prediksi vs. Nilai Aktual - Model Lengkap (77 Features)\n(Test Set)', 
                 fontsize=15, fontweight='bold', pad=20)
    ax.legend(loc='lower right', fontsize=11)
    ax.grid(True, alpha=0.3, linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Prediction vs Actual plot saved: {output_path}")
    print(f"   MAE: {mae:.2f} menit, R²: {r2:.4f}")
    plt.close()
    
    return mae, r2


def plot_residual_analysis_full_model(model, X_test, y_test, output_path='evaluation_results/residual_plot_final.png'):
    """
    Plot Residual Analysis menggunakan FULL MODEL (77 features)
    """
    # Prediksi menggunakan FULL MODEL
    y_pred = model.predict(X_test)
    residuals = y_test - y_pred
    
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
    
    # 1. Residual vs Predicted
    ax1.scatter(y_pred, residuals, alpha=0.5, s=30, c='coral', edgecolors='black', linewidth=0.5)
    ax1.axhline(y=0, color='r', linestyle='--', lw=2, label='Zero Residual')
    ax1.set_xlabel('Prediksi Model (menit)', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Residual (Aktual - Prediksi)', fontsize=12, fontweight='bold')
    ax1.set_title('Residual vs. Prediksi', fontsize=14, fontweight='bold')
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3, linestyle='--')
    
    # Add statistics
    mean_residual = residuals.mean()
    std_residual = residuals.std()
    textstr = f'Mean: {mean_residual:.2f} min\nStd: {std_residual:.2f} min'
    props = dict(boxstyle='round', facecolor='lightblue', alpha=0.8)
    ax1.text(0.05, 0.95, textstr, transform=ax1.transAxes, fontsize=11,
            verticalalignment='top', bbox=props, fontweight='bold')
    
    # 2. Residual Distribution (Histogram)
    ax2.hist(residuals, bins=50, color='lightgreen', edgecolor='black', alpha=0.7)
    ax2.axvline(x=0, color='r', linestyle='--', lw=2, label='Zero Residual')
    ax2.set_xlabel('Residual (menit)', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Frekuensi', fontsize=12, fontweight='bold')
    ax2.set_title('Distribusi Residual', fontsize=14, fontweight='bold')
    ax2.legend(loc='upper right')
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Overall title
    fig.suptitle('Analisis Residual - Model Lengkap (77 Features)', 
                 fontsize=16, fontweight='bold', y=1.02)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✅ Residual plot saved: {output_path}")
    print(f"   Mean residual: {mean_residual:.2f} min, Std: {std_residual:.2f} min")
    plt.close()


def main():
    """Main function untuk generate semua grafik"""
    
    print("="*80)
    print("📊 GENERATING THESIS GRAPHS (FULL MODEL - 77 FEATURES)")
    print("="*80)
    
    # 1. Load existing model
    print("\n1️⃣ Loading trained model...")
    model_path = Path('model_improved.pkl')
    feature_names_path = Path('feature_names_improved.pkl')
    
    if not (model_path.exists() and feature_names_path.exists()):
        print("❌ ERROR: Model not found!")
        print("   Please run train_model_improved.py first.")
        return
    
    model = joblib.load(model_path)
    feature_names = joblib.load(feature_names_path)
    print(f"   ✓ Model loaded: {len(feature_names)} features")
    
    # 2. Load and prepare test data
    print("\n2️⃣ Loading and preparing test data...")
    
    # Load data
    data_dir = Path('../Data Flexo CSV')
    df_flexo_all, total_files = load_and_concat_csv(data_dir)
    df_clean = load_repair_history(Path('RIWAYAT_PERBAIKAN_REALISTIC.csv'))
    df_merged = merge_production_with_repairs(df_flexo_all, df_clean)
    df_flexo = preprocess_with_outlier_filter(df_merged)
    print(f"   ✓ Data loaded: {len(df_flexo)} rows")
    
    # 3. Split data (use same random_state as training)
    print("\n3️⃣ Splitting data for evaluation...")
    from sklearn.model_selection import train_test_split
    
    X = df_flexo.drop(['Stop Time', 'Stop_Time_Original'], axis=1, errors='ignore')
    y = df_flexo['Stop Time']
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    print(f"   ✓ Test set: {len(X_test)} samples")
    
    # 4. Generate grafik
    print("\n4️⃣ Generating graphs...")
    print("\n   a) Feature Importance (Top 15)...")
    plot_feature_importance_top15(model, feature_names)
    
    print("\n   b) Prediction vs Actual (Full Model - 77 features)...")
    mae, r2 = plot_prediction_vs_actual_full_model(model, X_test, y_test)
    
    print("\n   c) Residual Analysis (Full Model - 77 features)...")
    plot_residual_analysis_full_model(model, X_test, y_test)
    
    # 5. Summary
    print("\n" + "="*80)
    print("✅ ALL GRAPHS GENERATED SUCCESSFULLY!")
    print("="*80)
    print(f"\n📊 Full Model Performance (77 Features):")
    print(f"   • MAE: {mae:.2f} menit")
    print(f"   • R²: {r2:.4f}")
    print(f"\n📁 Output files:")
    print(f"   • evaluation_results/feature_importance_final.png")
    print(f"   • evaluation_results/prediction_vs_actual_final.png")
    print(f"   • evaluation_results/residual_plot_final.png")
    print("\n🎓 Graphs ready for thesis documentation!")
    print("="*80)


if __name__ == "__main__":
    main()

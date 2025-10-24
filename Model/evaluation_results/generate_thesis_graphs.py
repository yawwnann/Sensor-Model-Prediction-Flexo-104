"""
Script untuk Generate Grafik Visualisasi Skripsi
Proyek: Sensor-Model-Prediction-Flexo-104

Fungsi:
1. Grafik Tren OEE Bulanan (Sept 2024 - Sept 2025)
2. Grafik Feature Importance Model Final
3. Grafik Prediksi vs Aktual Durasi Downtime
4. Grafik Residual Plot Model

Author: Generated for Thesis Chapter 4
Date: 2025
"""

import sys
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Import fungsi preprocessing dari train_model.py
from train_model import load_and_concat_csv, preprocess_for_machine

# Konfigurasi style untuk grafik yang lebih profesional
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")


def plot_monthly_oee(output_path="oee_trend.png"):
    """
    [Grafik 1] Tren OEE Bulanan (Data Manual)
    
    Membuat grafik garis yang menunjukkan tren Overall Equipment Effectiveness (OEE)
    bulanan untuk Flexo 104 dari September 2024 hingga September 2025.
    Data diambil dari Tabel 4.4 skripsi.
    
    Parameters:
    -----------
    output_path : str
        Path untuk menyimpan file grafik (default: "oee_trend.png")
    """
    print("\n" + "="*70)
    print("[GRAFIK 1] MEMBUAT TREN OEE BULANAN")
    print("="*70)
    
    # Data OEE bulanan dari Tabel 4.4 skripsi (Sept 2024 - Sept 2025)
    # Format: (Bulan-Tahun, Nilai OEE %)
    months = [
        "Sept 2024", "Okt 2024", "Nov 2024", "Des 2024",
        "Jan 2025", "Feb 2025", "Mar 2025", "Apr 2025",
        "Mei 2025", "Jun 2025", "Jul 2025", "Agu 2025", "Sept 2025"
    ]
    
    # Data OEE dalam persen (sesuaikan dengan data aktual dari skripsi Anda)
    # CATATAN: Ganti nilai-nilai ini dengan data aktual dari Tabel 4.4 skripsi Anda
    oee_values = [
        82.5, 81.3, 79.8, 78.2,  # Sept-Des 2024
        80.1, 82.7, 84.2, 83.5,  # Jan-Apr 2025
        85.3, 86.1, 84.9, 83.8, 82.4  # Mei-Sept 2025
    ]
    
    # PERINGATAN: Pastikan untuk mengganti nilai OEE di atas dengan data real!
    print("⚠️  PERINGATAN: Pastikan data OEE sudah sesuai dengan Tabel 4.4 skripsi Anda!")
    print(f"   Jumlah data: {len(oee_values)} bulan")
    
    # Buat figure dengan ukuran yang sesuai
    fig, ax = plt.subplots(figsize=(14, 7))
    
    # Plot grafik garis OEE
    line = ax.plot(months, oee_values, 
                   marker='o', 
                   linewidth=2.5, 
                   markersize=8,
                   color='#2E86AB',
                   label='OEE Aktual')
    
    # Tambahkan garis horizontal standar world class (85%)
    ax.axhline(y=85, color='#A23B72', linestyle='--', linewidth=2, 
               label='Standar World Class (85%)', alpha=0.7)
    
    # Konfigurasi sumbu dan label
    ax.set_xlabel('Bulan-Tahun', fontsize=12, fontweight='bold')
    ax.set_ylabel('Nilai OEE (%)', fontsize=12, fontweight='bold')
    ax.set_title('Tren Overall Equipment Effectiveness (OEE) Bulanan Flexo 104\n(September 2024 - September 2025)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Rotasi label sumbu X agar tidak tumpang tindih
    ax.set_xticklabels(months, rotation=45, ha='right')
    
    # Tambahkan grid untuk kemudahan pembacaan
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Tambahkan nilai pada setiap titik data
    for i, (month, oee) in enumerate(zip(months, oee_values)):
        ax.annotate(f'{oee:.1f}%', 
                   xy=(i, oee), 
                   xytext=(0, 10),
                   textcoords='offset points',
                   ha='center',
                   fontsize=9,
                   bbox=dict(boxstyle='round,pad=0.3', facecolor='yellow', alpha=0.3))
    
    # Set batas sumbu Y dengan margin
    y_min = min(oee_values) - 5
    y_max = max(max(oee_values), 85) + 5
    ax.set_ylim(y_min, y_max)
    
    # Tambahkan legend
    ax.legend(loc='best', fontsize=11, framealpha=0.9)
    
    # Tight layout untuk memastikan semua elemen terlihat
    plt.tight_layout()
    
    # Simpan grafik
    output_file = Path(output_path)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"✓ Grafik tren OEE berhasil disimpan ke: {output_file.absolute()}")
    
    # Hitung statistik deskriptif
    print(f"\nStatistik OEE:")
    print(f"  - OEE Rata-rata  : {np.mean(oee_values):.2f}%")
    print(f"  - OEE Tertinggi  : {np.max(oee_values):.2f}% ({months[np.argmax(oee_values)]})")
    print(f"  - OEE Terendah   : {np.min(oee_values):.2f}% ({months[np.argmin(oee_values)]})")
    print(f"  - Standar Deviasi: {np.std(oee_values):.2f}%")
    
    # Hitung berapa bulan mencapai world class
    world_class_count = sum(1 for oee in oee_values if oee >= 85)
    print(f"  - Bulan mencapai World Class (≥85%): {world_class_count}/{len(oee_values)}")
    
    plt.close()
    

def plot_feature_importance(model_dir=".", output_path="feature_importance.png"):
    """
    [Grafik 2] Feature Importance Model Final
    
    Membuat grafik batang horizontal yang menunjukkan Top 15 fitur paling penting
    dari model prediksi durasi downtime.
    
    Parameters:
    -----------
    model_dir : str
        Direktori yang berisi model.pkl dan feature_names.pkl
    output_path : str
        Path untuk menyimpan file grafik
    """
    print("\n" + "="*70)
    print("[GRAFIK 2] MEMBUAT FEATURE IMPORTANCE MODEL FINAL")
    print("="*70)
    
    model_dir = Path(model_dir)
    
    # Load model dan nama fitur
    model_path = model_dir / "model.pkl"
    feature_names_path = model_dir / "feature_names.pkl"
    
    if not model_path.exists():
        raise FileNotFoundError(f"Model tidak ditemukan di: {model_path}")
    if not feature_names_path.exists():
        raise FileNotFoundError(f"Feature names tidak ditemukan di: {feature_names_path}")
    
    print(f"Memuat model dari: {model_path.name}")
    model = joblib.load(model_path)
    
    print(f"Memuat nama fitur dari: {feature_names_path.name}")
    feature_names = joblib.load(feature_names_path)
    
    # Dapatkan feature importances
    importances = model.feature_importances_
    
    # Buat DataFrame
    feature_importance_df = pd.DataFrame({
        'Feature': feature_names,
        'Importance': importances
    })
    
    # Urutkan berdasarkan importance (descending)
    feature_importance_df = feature_importance_df.sort_values('Importance', ascending=False)
    
    # Ambil Top 15 fitur
    top_n = 15
    top_features = feature_importance_df.head(top_n)
    
    print(f"\nTop {top_n} Fitur Terpenting:")
    for idx, row in top_features.iterrows():
        print(f"  {row['Importance']:.4f} - {row['Feature']}")
    
    # Buat grafik
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Buat horizontal bar plot
    bars = ax.barh(range(len(top_features)), top_features['Importance'], color='steelblue')
    
    # Tambahkan gradient color (fitur terpenting lebih gelap)
    colors = plt.cm.Blues(np.linspace(0.4, 0.8, len(top_features)))
    for bar, color in zip(bars, colors):
        bar.set_color(color)
    
    # Set tick labels dengan nama fitur
    ax.set_yticks(range(len(top_features)))
    
    # Format nama fitur agar lebih readable (hapus prefix, ganti underscore)
    formatted_labels = []
    for feat in top_features['Feature']:
        # Hapus prefix yang panjang
        if feat.startswith('Scrab Description_'):
            label = feat.replace('Scrab Description_', 'Scrap: ')
        elif feat.startswith('Break Time Description_'):
            label = feat.replace('Break Time Description_', 'Break: ')
        elif feat.startswith('Shift_'):
            label = feat.replace('Shift_', 'Shift ')
        else:
            label = feat
        
        # Ganti underscore dengan spasi dan batasi panjang
        label = label.replace('_', ' ')
        if len(label) > 50:
            label = label[:47] + '...'
        
        formatted_labels.append(label)
    
    ax.set_yticklabels(formatted_labels)
    
    # Invert y-axis agar fitur terpenting di atas
    ax.invert_yaxis()
    
    # Label dan judul
    ax.set_xlabel('Importance Score', fontsize=12, fontweight='bold')
    ax.set_ylabel('Nama Fitur', fontsize=12, fontweight='bold')
    ax.set_title('Top 15 Fitur Penting Model Prediksi Durasi Downtime\n(RandomForest Regressor)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Tambahkan grid untuk kemudahan pembacaan
    ax.grid(True, alpha=0.3, linestyle='--', axis='x')
    
    # Tambahkan nilai importance pada setiap bar
    for i, (bar, importance) in enumerate(zip(bars, top_features['Importance'])):
        width = bar.get_width()
        ax.text(width, bar.get_y() + bar.get_height()/2, 
                f' {importance:.4f}',
                ha='left', va='center', fontsize=9, fontweight='bold')
    
    plt.tight_layout()
    
    # Simpan grafik
    output_file = Path(output_path)
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\n✓ Grafik feature importance berhasil disimpan ke: {output_file.absolute()}")
    
    # Tampilkan statistik
    total_importance = top_features['Importance'].sum()
    print(f"\nStatistik Feature Importance:")
    print(f"  - Total importance Top 15: {total_importance:.4f} ({total_importance*100:.2f}%)")
    print(f"  - Total fitur model      : {len(feature_names)}")
    
    plt.close()


def plot_prediction_analysis(data_dir="../Data Flexo CSV", 
                            output_scatter="prediction_vs_actual.png", 
                            output_residual="residual_plot.png"):
    """
    [Grafik 3 & 4] Prediksi vs. Aktual & Residual Plot
    
    Membuat dua grafik:
    1. Scatter plot Prediksi vs Aktual durasi downtime
    2. Residual plot untuk analisis error model
    
    Parameters:
    -----------
    data_dir : str
        Direktori yang berisi file CSV data
    output_scatter : str
        Path untuk menyimpan grafik prediksi vs aktual
    output_residual : str
        Path untuk menyimpan grafik residual
    """
    print("\n" + "="*70)
    print("[GRAFIK 3 & 4] MEMBUAT PREDIKSI VS AKTUAL & RESIDUAL PLOT")
    print("="*70)
    
    # Load dan preprocess data menggunakan fungsi dari train_model.py
    print("\nMemuat dan memproses data...")
    data_dir = Path(data_dir)
    
    try:
        # Load data CSV
        combined_df, file_count = load_and_concat_csv(data_dir)
        print(f"✓ Berhasil memuat {file_count} file CSV")
        print(f"  Total baris data: {len(combined_df)}")
        
        # Preprocess untuk Flexo 104
        processed_df = preprocess_for_machine(combined_df, work_center="C_FL104")
        print(f"✓ Data untuk C_FL104: {len(processed_df)} baris")
        
    except Exception as e:
        print(f"✗ Error memuat data: {e}")
        raise
    
    # Persiapan fitur dan target
    print("\nMempersiapkan fitur dan target...")
    
    # Target (y): Waktu Downtime
    y = processed_df["Waktu Downtime (Menit)"]
    
    # Fitur (X): Drop kolom yang tidak diperlukan (sama seperti di train_model.py)
    features_to_drop = [
        'Waktu Downtime (Menit)',
        'Work Center',
        'Scrab Description',
        'Break Time Description',
        'Shift',
        'Total Produksi (Pcs)',
        'Produk Cacat (Pcs)',
        'Quality_Rate',
        'Availability_Rate',
        'Posting Date',
        'Machine',
        'Group',
        'Prod Order',
        'Confirm KG',
        'Act Confirm KG',
        'Scrab KG',
        'Start.Date',
        'Start.Time',
        'Finis.Time',
        'Finis.Date'
    ]
    
    cols_to_drop = [col for col in features_to_drop if col in processed_df.columns]
    X = processed_df.drop(columns=cols_to_drop)
    
    # Filter hanya kolom numerik
    numeric_cols = X.select_dtypes(include=[np.number]).columns
    X = X[numeric_cols]
    
    print(f"✓ Jumlah fitur: {len(X.columns)}")
    print(f"✓ Jumlah sampel: {len(X)}")
    
    # Train-test split
    print("\nMembagi data (80% training, 20% testing)...")
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"✓ Data training: {len(X_train)} baris")
    print(f"✓ Data testing : {len(X_test)} baris")
    
    # Latih model pada data training
    print("\nMelatih RandomForest model...")
    model = RandomForestRegressor(
        n_estimators=100,
        random_state=42,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        n_jobs=-1
    )
    model.fit(X_train, y_train)
    print("✓ Model berhasil dilatih")
    
    # Prediksi pada test set
    print("\nMelakukan prediksi pada test set...")
    y_pred = model.predict(X_test)
    
    # Hitung metrik evaluasi
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_test, y_pred)
    
    print(f"\nMetrik Evaluasi Model:")
    print(f"  - MAE  : {mae:.4f} menit")
    print(f"  - RMSE : {rmse:.4f} menit")
    print(f"  - R²   : {r2:.4f}")
    
    # ========================================================================
    # GRAFIK 3: Prediksi vs Aktual
    # ========================================================================
    print("\n[GRAFIK 3] Membuat scatter plot Prediksi vs Aktual...")
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Scatter plot
    scatter = ax.scatter(y_test, y_pred, alpha=0.6, s=50, 
                        c=y_test, cmap='viridis', edgecolors='black', linewidth=0.5)
    
    # Garis diagonal perfect prediction (y=x)
    min_val = min(y_test.min(), y_pred.min())
    max_val = max(y_test.max(), y_pred.max())
    ax.plot([min_val, max_val], [min_val, max_val], 
            'r--', linewidth=2.5, label='Perfect Prediction (y=x)', alpha=0.8)
    
    # Konfigurasi sumbu dan label
    ax.set_xlabel('Durasi Downtime Aktual (Menit)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Durasi Downtime Prediksi (Menit)', fontsize=12, fontweight='bold')
    ax.set_title('Prediksi vs. Nilai Aktual Durasi Downtime (Test Set)\nModel RandomForest Regressor', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Tambahkan grid
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Tambahkan colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Durasi Aktual (Menit)', fontsize=10)
    
    # Tambahkan informasi metrik di grafik
    textstr = f'R² = {r2:.4f}\nMAE = {mae:.2f} menit\nRMSE = {rmse:.2f} menit'
    props = dict(boxstyle='round', facecolor='wheat', alpha=0.8)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=props)
    
    # Legend
    ax.legend(loc='lower right', fontsize=10)
    
    plt.tight_layout()
    
    # Simpan grafik
    output_file_scatter = Path(output_scatter)
    plt.savefig(output_file_scatter, dpi=300, bbox_inches='tight')
    print(f"✓ Grafik Prediksi vs Aktual disimpan ke: {output_file_scatter.absolute()}")
    
    plt.close()
    
    # ========================================================================
    # GRAFIK 4: Residual Plot
    # ========================================================================
    print("\n[GRAFIK 4] Membuat residual plot...")
    
    # Hitung residuals
    residuals = y_test - y_pred
    
    fig, ax = plt.subplots(figsize=(10, 8))
    
    # Scatter plot residuals
    scatter = ax.scatter(y_pred, residuals, alpha=0.6, s=50,
                        c=residuals, cmap='coolwarm', edgecolors='black', linewidth=0.5)
    
    # Garis horizontal pada y=0 (no error)
    ax.axhline(y=0, color='red', linestyle='--', linewidth=2.5, 
               label='Zero Error', alpha=0.8)
    
    # Tambahkan garis ±2 standar deviasi untuk outlier detection
    std_residual = np.std(residuals)
    ax.axhline(y=2*std_residual, color='orange', linestyle=':', linewidth=2, 
               label=f'±2σ ({2*std_residual:.2f} menit)', alpha=0.6)
    ax.axhline(y=-2*std_residual, color='orange', linestyle=':', linewidth=2, alpha=0.6)
    
    # Konfigurasi sumbu dan label
    ax.set_xlabel('Durasi Downtime Prediksi (Menit)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Residual / Error (Aktual - Prediksi, Menit)', fontsize=12, fontweight='bold')
    ax.set_title('Plot Residual Model Prediksi Durasi Downtime\nAnalisis Error Prediksi', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Tambahkan grid
    ax.grid(True, alpha=0.3, linestyle='--')
    
    # Tambahkan colorbar
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Residual (Menit)', fontsize=10)
    
    # Tambahkan informasi statistik residual di grafik
    mean_residual = np.mean(residuals)
    median_residual = np.median(residuals)
    textstr = (f'Mean Error = {mean_residual:.2f} menit\n'
              f'Median Error = {median_residual:.2f} menit\n'
              f'Std Dev = {std_residual:.2f} menit')
    props = dict(boxstyle='round', facecolor='lightblue', alpha=0.8)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=11,
            verticalalignment='top', bbox=props)
    
    # Legend
    ax.legend(loc='upper right', fontsize=10)
    
    plt.tight_layout()
    
    # Simpan grafik
    output_file_residual = Path(output_residual)
    plt.savefig(output_file_residual, dpi=300, bbox_inches='tight')
    print(f"✓ Grafik Residual Plot disimpan ke: {output_file_residual.absolute()}")
    
    # Analisis residual
    print(f"\nAnalisis Residual:")
    print(f"  - Mean error     : {mean_residual:.4f} menit (idealnya ~0)")
    print(f"  - Median error   : {median_residual:.4f} menit")
    print(f"  - Std deviation  : {std_residual:.4f} menit")
    print(f"  - Min residual   : {residuals.min():.4f} menit")
    print(f"  - Max residual   : {residuals.max():.4f} menit")
    
    # Hitung persentase data dalam ±2σ (normalitas check)
    within_2sigma = np.sum(np.abs(residuals) <= 2*std_residual) / len(residuals) * 100
    print(f"  - Data dalam ±2σ : {within_2sigma:.2f}% (idealnya ~95%)")
    
    plt.close()


def main():
    """
    Fungsi utama untuk generate semua grafik thesis
    """
    print("\n" + "="*70)
    print("GENERATE GRAFIK VISUALISASI SKRIPSI")
    print("Proyek: Sensor-Model-Prediction-Flexo-104")
    print("="*70)
    
    # Path ke folder Model (tempat script ini berada)
    script_dir = Path(__file__).resolve().parent
    
    # Path ke folder Data CSV (satu level di atas, lalu masuk ke Data Flexo CSV)
    data_dir = script_dir.parent / "Data Flexo CSV"
    
    # Cek apakah data directory ada
    if not data_dir.exists():
        print(f"\n✗ Error: Data directory tidak ditemukan di: {data_dir}")
        print("   Pastikan folder 'Data Flexo CSV' ada di parent directory.")
        sys.exit(1)
    
    print(f"\nKonfigurasi Path:")
    print(f"  - Script directory : {script_dir}")
    print(f"  - Data directory   : {data_dir}")
    print(f"  - Output directory : {script_dir}")
    
    try:
        # Grafik 1: Tren OEE Bulanan
        plot_monthly_oee(output_path=script_dir / "oee_trend.png")
        
        # Grafik 2: Feature Importance
        plot_feature_importance(
            model_dir=script_dir,
            output_path=script_dir / "feature_importance.png"
        )
        
        # Grafik 3 & 4: Prediksi vs Aktual & Residual
        plot_prediction_analysis(
            data_dir=data_dir,
            output_scatter=script_dir / "prediction_vs_actual.png",
            output_residual=script_dir / "residual_plot.png"
        )
        
        print("\n" + "="*70)
        print("✓ SEMUA GRAFIK BERHASIL DIBUAT")
        print("="*70)
        print(f"\nFile grafik tersimpan di: {script_dir}")
        print(f"  1. oee_trend.png              - Tren OEE Bulanan")
        print(f"  2. feature_importance.png     - Top 15 Fitur Penting")
        print(f"  3. prediction_vs_actual.png   - Prediksi vs Aktual")
        print(f"  4. residual_plot.png          - Residual Plot")
        print("\n✓ Grafik siap digunakan untuk Bab 4 skripsi Anda!")
        print("="*70)
        
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

import sys
from pathlib import Path
import glob
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
import joblib
from datetime import datetime

# Konstanta untuk perhitungan OEE
TOTAL_SHIFT_TIME_MINUTES = 480.0  # 8 jam = 480 menit

# ============================================================================
# MAPPING FMEA SEVERITY (Skor S dari Analisis FMEA Tabel 4.5 Skripsi)
# ============================================================================
# Mapping dari Deskripsi Downtime ke Skor Severity (S) FMEA
# Skor 1-10: 1=sangat ringan, 10=sangat parah/berbahaya
# 
# CATATAN PENTING: Mapping ini dibuat berdasarkan estimasi dampak bisnis
# dan harus divalidasi/disesuaikan dengan Tabel 4.5 FMEA dari skripsi Anda.
FMEA_SEVERITY_MAP = {
    # ========================================================================
    # PRE-FEEDER UNIT FAILURES (S = 6-8)
    # ========================================================================
    'BELT CONVEYOR SLIP': 7,                    # Belt slip - menghambat feeding
    'PENUMPUKAN KARTON TIDAK RATA': 7,          # Penumpukan tidak rata - waste tinggi
    'SENSOR TIDAK MENDETEKSI LEMBARAN': 8,      # Sensor error - stop produksi total
    
    # ========================================================================
    # FEEDER UNIT FAILURES (S = 7-9)
    # ========================================================================
    'FEEDER UNIT TROUBLE MEKANIK': 8,           # Kerusakan mekanik - perbaikan lama
    'FEEDER UNIT TROUBLE ELEKTRIK': 8,          # Kerusakan elektrik - downtime signifikan
    'VACUM KURANG': 8,                          # Vakum lemah - feeding error berulang
    'VACUUM KURANG': 8,                         # Variant spelling
    'SHEET NYANGKUT/ MACET': 7,                 # Sheet macet - dapat diperbaiki cepat
    'LEMBARAN TIDAK TERAMBIL': 8,               # Feed failure - stop produksi
    
    # ========================================================================
    # PRINTING UNIT FAILURES (S = 8-10)
    # ========================================================================
    'PRINTING UNIT TROUBLE MEKANIK': 9,         # Kerusakan printing - defect rate tinggi
    'PRINTING UNIT TROUBLE ELEKTRIK': 9,        # Elektrik printing - downtime panjang
    'REGISTER GESER': 9,                        # Misalignment - reject rate sangat tinggi
    'PRINT BLOBOR': 9,                          # Ink blobbing - waste besar
    'PRINTING BOTAK': 8,                        # Incomplete print - defect sedang-tinggi
    'PRINT LARI': 8,                            # Print offset - adjustment needed
    'PRINT BLUR': 8,                            # Print blur - quality issue
    'TINTA BOCOR': 8,                           # Ink leak - downtime + waste
    'LIMBAH TINTA BANJIR': 8,                   # Ink flooding - cleanup + downtime
    'WARNA TIDAK SESUAI': 7,                    # Color mismatch - rework/reject
    'WARNA LUNTUR': 7,                          # Color fade - quality issue
    'TINTA TIDAK KONSISTEN': 8,                 # Ink inconsistency - defect tinggi
    'ANILOX ROLLER TERSUMBAT': 8,               # Anilox blocked - print quality issue
    
    # ========================================================================
    # SLOTTER & CREASING UNIT FAILURES (S = 7-9)
    # ========================================================================
    'SLOTTER UNIT TROUBLE MEKANIK': 8,          # Slotter mechanical - structural damage
    'SLOTTER UNIT TROUBLE ELEKTRIK': 9,         # Slotter electrical - stop total
    'SLOTER LARI': 8,                           # Slotter misalignment - reject tinggi
    'SLOTTER LARI': 8,                          # Variant spelling
    'SLOTTER MIRING': 8,                        # Slotter angle error - defect
    'SLOTTER PECAH': 9,                         # Slotter crack - product unusable
    'PISAU TUMPUL': 8,                          # Dull blade - quality degradation
    'CREASING PECAH': 9,                        # Creasing crack - product failure
    'CREASING LARI': 8,                         # Creasing offset - folding issues
    'CREASING MIRING': 8,                       # Creasing angle - assembly problems
    'ROLLER CREASING AUS': 8,                   # Worn creasing roller
    
    # ========================================================================
    # DIE-CUT UNIT FAILURES (S = 7-9)
    # ========================================================================
    'DIECUT UNIT TROUBLE MEKANIK': 8,           # Die-cut mechanical failure
    'DIECUT UNIT TROUBLE ELEKTRIK': 9,          # Die-cut electrical failure
    'DIECUT LARI': 8,                           # Die-cut misalignment
    'DIECUT PECAH': 9,                          # Die-cut crack - unusable
    'DIECUT TIDAK PUTUS': 8,                    # Incomplete die-cut
    'DIECUT MIRING': 8,                         # Die-cut angle error
    
    # ========================================================================
    # STACKER UNIT FAILURES (S = 5-8)
    # ========================================================================
    'STACKER TROUBLE MEKANIK': 6,               # Stacker mechanical - minor impact
    'STACKER TROUBLE ELEKTRIK': 9,              # Stacker electrical - stop produksi
    'COUNTER PROBLEM': 6,                       # Counter error - tracking issue saja
    'SENSOR PENGHITUNG ERROR': 6,               # Count sensor error
    'PNEUMATIC LEMAH': 6,                       # Weak pneumatic
    'CONVEYOR SLIP': 6,                         # Conveyor slip di stacker
    
    # ========================================================================
    # PLATE & SETUP ISSUES (S = 4-7)
    # ========================================================================
    'LAP KLISE (Plate)': 4,                     # Plate cleaning - planned maintenance
    'MOUNTING PLATE (during operati': 5,        # Plate mounting - setup time
    'GANTI/PASANG PISAU SLOTTER': 5,            # Blade change - setup
    'PLATE CYLINDER TIDAK SEJAJAR': 9,          # Plate misalignment - critical
    
    # ========================================================================
    # MATERIAL & SUPPLY ISSUES (S = 5-7)
    # ========================================================================
    'TUNGGU TINTA': 6,                          # Waiting ink - supply delay
    'TUNGGU BAHAN SHEETS': 6,                   # Waiting sheets - supply chain
    'CARI BAHAN SHEETS': 6,                     # Looking for sheets
    'TUNGGU KLISE (Plate)': 6,                  # Waiting plate
    'CHEMICAL PROBLEM>OTHERS': 7,               # Chemical issue - quality impact
    
    # ========================================================================
    # OPERATIONAL & MAINTENANCE (S = 2-5)
    # ========================================================================
    'SETTING TIME': 3,                          # Setup time - normal operation
    'ADJUST TINTA': 4,                          # Ink adjustment - fine tuning
    'REPAIR RINGAN BY OPERATOR': 5,             # Minor repair by operator
    'MECHANICAL REPAIR>OTHER': 6,               # Mechanical repair - general
    'BUANG SAMPAH': 2,                          # Waste disposal - routine
    'CUCI MESIN': 3,                            # Machine cleaning - maintenance
    'RAPIH SHIFT': 2,                           # Shift cleanup
    'BRIEFING': 1,                              # Meeting - planned
    'SHOLAT JUMAT': 1,                          # Friday prayer - scheduled
    'ISTIRAHAT': 1,                             # Break - scheduled
    
    # ========================================================================
    # PLANNED DOWNTIME (S = 1-3)
    # ========================================================================
    'TIDAK ADA SHIFT': 1,                       # No shift - planned
    'OFF TIME LIBUR NASIONAL': 1,               # National holiday
    'TUNGGU ORDER': 2,                          # Waiting order - business decision
    'SCHEDULED PREVENTIVE MAINTENANCE': 2,      # Planned maintenance
    'OVERHAUL': 3,                              # Major overhaul - planned
    
    # ========================================================================
    # QUALITY REJECTION ISSUES (S = 6-8)
    # ========================================================================
    'REJECT SETTING': 7,                        # Setup rejection - waste
    'OTHERS REJECTED SHEETS': 7,                # General rejection
    'REJECTED KARTON': 7,                       # Rejected carton
    
    # ========================================================================
    # OTHERS & DEFAULT (S = 5)
    # ========================================================================
    'OTHERS': 5,                                # General others - medium severity
    '_NONE_': 1,                                # No reason - minimal severity
}

# Skor default jika deskripsi tidak ditemukan di map
DEFAULT_SEVERITY = 5  # Medium severity sebagai fallback


def sort_files_by_month(files: list) -> list:
    """
    Mengurutkan file berdasarkan bulan dari September 2024 hingga September 2025.
    Pola nama file: "Laporan Flexo [Bulan] [Tahun].csv" atau "Produksi Bulan [Bulan] [Tahun].XLSX"
    """
    month_names = ["september", "oktober", "november", "desember",
                   "januari", "februari", "maret", "april",
                   "mei", "juni", "juli", "agustus"]
    
    def get_sort_key(filepath):
        filename = Path(filepath).stem.lower()
        
        # Ekstrak bulan dari nama file
        month_idx = None
        for idx, month_name in enumerate(month_names):
            if month_name in filename:
                month_idx = idx
                break
        
        if month_idx is None:
            return (9999, 9999)  # File yang tidak cocok akan di akhir
        
        # Tentukan tahun berdasarkan bulan
        # September 2024 (idx=0) -> year=2024
        # Oktober-Desember 2024 (idx=1-3) -> year=2024
        # Januari-Agustus 2025 (idx=4-11) -> year=2025
        # September 2025 (idx=0 dengan 2025) -> year=2025
        
        year = 2024
        sort_month = month_idx
        
        # Jika "2024" atau "2025" ada di nama file, gunakan itu
        if "2024" in filename:
            year = 2024
        elif "2025" in filename:
            year = 2025
            # Jika September 2025, tambah offset agar setelah Agustus 2025
            if month_idx == 0:  # September
                sort_month = 12
        else:
            # Jika tidak ada tahun eksplisit, gunakan logika default
            if month_idx <= 3:  # September - Desember
                year = 2024
            else:  # Januari - Agustus
                year = 2025
        
        return (year, sort_month)
    
    return sorted(files, key=get_sort_key)


def load_and_concat_csv(data_dir: Path, pattern: str = "Laporan Flexo *.csv") -> tuple[pd.DataFrame, int]:
    """
    Memuat semua file CSV yang cocok dengan pola, lalu menggabungkannya.
    File diurutkan berdasarkan bulan (September 2024 - September 2025).
    Mengembalikan (dataframe_gabungan, jumlah_file_terbaca).
    """
    data_dir = Path(data_dir)
    files = glob.glob(str(data_dir / pattern))

    if not files:
        raise FileNotFoundError(f"Tidak ditemukan file dengan pola '{pattern}' di folder: {data_dir}")

    # Urutkan file berdasarkan bulan
    files = sort_files_by_month(files)

    frames = []
    for f in files:
        try:
            # Membaca CSV dengan pemisah titik koma (;)
            df = pd.read_csv(f, encoding="utf-8-sig", delimiter=';')
            frames.append(df)
            print(f"  ✓ Memuat: {Path(f).name}")
        except Exception as e:
            print(f"  ✗ Gagal memuat {Path(f).name}: {e}")
            continue

    if not frames:
        raise ValueError("Tidak ada data yang berhasil dibaca dari file CSV.")
        
    combined = pd.concat(frames, ignore_index=True)
    return combined, len(frames)


def get_fmea_severity(scrab_desc: str, break_desc: str) -> int:
    """
    Mendapatkan skor FMEA Severity berdasarkan deskripsi downtime.
    
    Prioritas:
    1. Scrab Description (jika ada) - lebih spesifik ke kualitas produk
    2. Break Time Description (jika Scrab kosong) - alasan downtime umum
    3. DEFAULT_SEVERITY jika keduanya kosong atau tidak ditemukan
    
    Args:
        scrab_desc: Scrab Description dari data
        break_desc: Break Time Description dari data
        
    Returns:
        int: Skor severity 1-10 (1=ringan, 10=sangat parah)
    """
    # Normalisasi: strip whitespace dan uppercase
    scrab = str(scrab_desc).strip().upper() if pd.notna(scrab_desc) else ''
    break_time = str(break_desc).strip().upper() if pd.notna(break_desc) else ''
    
    # Prioritas 1: Cek Scrab Description (lebih spesifik)
    if scrab and scrab != '_NONE_' and scrab != 'NAN':
        if scrab in FMEA_SEVERITY_MAP:
            return FMEA_SEVERITY_MAP[scrab]
    
    # Prioritas 2: Cek Break Time Description
    if break_time and break_time != '_NONE_' and break_time != 'NAN':
        if break_time in FMEA_SEVERITY_MAP:
            return FMEA_SEVERITY_MAP[break_time]
    
    # Default: Tidak ditemukan di map
    return DEFAULT_SEVERITY


def preprocess_for_machine(df: pd.DataFrame, work_center: str = "C_FL104") -> pd.DataFrame:
    """
    Filter hanya untuk work center tertentu dan bersihkan data.
    Menerapkan feature engineering canggih:
    1. Mapping kolom dasar
    2. Perhitungan fitur OEE (Quality Rate & Availability Rate)
    3. One-hot encoding fitur kategorikal (Scrab Description & Break Time Description)
    4. FMEA Severity scoring (FITUR BARU)
    
    Mapping kolom dari nama asli ke nama yang diharapkan:
    - Work Center -> Work Center (tetap sama)
    - Confirm Qty -> Total Produksi (Pcs)
    - Scrab Qty -> Produk Cacat (Pcs)
    - Stop Time -> Waktu Downtime (Menit)
    """
    # Mapping kolom dari nama asli ke nama yang diharapkan
    col_mapping = {
        "Confirm Qty": "Total Produksi (Pcs)",
        "Scrab Qty": "Produk Cacat (Pcs)",
        "Stop Time": "Waktu Downtime (Menit)",
    }

    # Periksa kolom yang ada
    required_cols = ["Work Center"] + list(col_mapping.keys())
    available_cols = [c for c in required_cols if c in df.columns]
    if len(available_cols) < len(required_cols):
        missing = [c for c in required_cols if c not in df.columns]
        raise KeyError(f"Kolom wajib hilang pada data: {missing}")

    # Rename kolom
    df_renamed = df.rename(columns=col_mapping).copy()

    # Filter berdasarkan Work Center
    filtered = df_renamed[df_renamed["Work Center"].astype(str).str.strip() == work_center].copy()
    if filtered.empty:
        raise ValueError(f"Tidak ada data ditemukan untuk Work Center '{work_center}'.")
    
    # ========================================================================
    # FILTER KRITIS: Hapus Baris Ringkasan/Summary (Data Kontaminasi)
    # ========================================================================
    # Baris ringkasan memiliki Stop Time tinggi tetapi TIDAK memiliki alasan downtime.
    # Ini menyebabkan model belajar korelasi palsu (produksi tinggi = downtime tinggi).
    # Kita HANYA ingin data kejadian downtime yang sebenarnya dengan alasan yang jelas.
    print("\n  → Memfilter data kontaminasi (baris ringkasan tanpa alasan downtime)...")
    original_row_count = len(filtered)
    
    # Filter: Simpan HANYA baris yang memiliki Scrab Description ATAU Break Time Description
    # (Baris ringkasan memiliki KEDUA kolom ini kosong/NaN)
    filtered = filtered[
        filtered['Scrab Description'].notna() | 
        filtered['Break Time Description'].notna()
    ].copy()
    
    new_row_count = len(filtered)
    removed_rows = original_row_count - new_row_count
    
    print(f"     ✓ Data sebelum filter: {original_row_count} baris")
    print(f"     ✓ Data setelah filter: {new_row_count} baris")
    print(f"     ✓ Baris ringkasan dihapus: {removed_rows} baris")
    
    if new_row_count == 0:
        raise ValueError(f"Tidak ada data kejadian downtime yang valid setelah filter.")
    
    # Konversi tipe numerik yang diperlukan (coerce agar error menjadi NaN)
    numeric_cols = ["Total Produksi (Pcs)", "Produk Cacat (Pcs)", "Waktu Downtime (Menit)"]
    for c in numeric_cols:
        filtered[c] = pd.to_numeric(filtered[c], errors="coerce")

    # Hapus baris yang datanya tidak valid (kosong) pada kolom-kolom penting
    filtered = filtered.dropna(subset=numeric_cols)
    
    # ========================================================================
    # FILTER KRITIS 2: Buat "Model Spesialis Kerusakan"
    # ========================================================================
    # Hapus downtime operasional/terjadwal agar model HANYA belajar dari
    # data kerusakan mesin (break/fix). Ini membuat prediksi lebih realistis.
    print("\n  → Membuat 'Model Spesialis' (hanya data break/fix kerusakan mesin)...")
    
    # Daftar downtime operasional/terjadwal yang harus dihapus
    PLANNED_DOWNTIME_BLACKLIST = [
        'TIDAK ADA SHIFT',
        'OFF TIME LIBUR NASIONAL',
        'TUNGGU ORDER',
        'SCHEDULED PREVENTIVE MAINTENANCE',
        'BRIEFING',
        'BUANG SAMPAH',
        'CARI BAHAN SHEETS',
        'TUNGGU BAHAN SHEETS',
        'ISTIRAHAT',
        'TUNGGU KLISE (Plate)',
        'LAP KLISE (Plate)',
        'SETTING TIME',
        'ADJUST TINTA',
        '_NONE_',  # Baris tanpa alasan jelas
        'OVERHAUL',  # Maintenance terjadwal
        'CUCI MESIN',
        'RAPIH SHIFT'
    ]
    
    operational_rows_before = len(filtered)
    
    # Filter: Hapus baris dengan Break Time Description yang ada di blacklist
    # TETAPI simpan SEMUA baris dengan Scrab Description (ini semua kerusakan)
    filtered = filtered[
        ~filtered['Break Time Description'].isin(PLANNED_DOWNTIME_BLACKLIST) | 
        filtered['Scrab Description'].notna()
    ].copy()
    
    operational_rows_after = len(filtered)
    removed_operational = operational_rows_before - operational_rows_after
    
    print(f"     ✓ Data sebelum filter operasional: {operational_rows_before} baris")
    print(f"     ✓ Baris downtime operasional dihapus: {removed_operational} baris")
    print(f"     ✓ Total data 'break/fix' untuk training: {operational_rows_after} baris")
    
    if operational_rows_after == 0:
        raise ValueError(f"Tidak ada data kerusakan (break/fix) yang valid setelah filter.")
    
    # ========================================================================
    # FEATURE ENGINEERING: DIHAPUS - Tidak menggunakan fitur OEE/Produksi
    # ========================================================================
    # Model "Murni Fishbone" - HANYA belajar dari alasan downtime (kategorikal)
    # 
    # DIHAPUS:
    # - Quality_Rate: Bisa menyebabkan kebocoran data (calculated dari produksi)
    # - Availability_Rate: Kebocoran data langsung dari target variable
    # - Total Produksi, Produk Cacat: Bisa menyebabkan korelasi palsu
    #
    # Model ini akan MEMAKSA RandomForest untuk belajar 100% dari pola
    # "Alasan Downtime" (Fishbone Analysis).
    
    print("\n  → Melewati perhitungan fitur OEE...")
    print(f"     ⚠ Model 'Murni Fishbone': Tidak menggunakan fitur produksi/OEE")
    print(f"     ✓ Model akan belajar 100% dari fitur kategorikal (alasan downtime)")
    
    # ========================================================================
    # FEATURE ENGINEERING: FMEA Severity Scoring (FITUR BARU)
    # ========================================================================
    print("\n  → Menghitung FMEA Severity Score untuk setiap downtime...")
    
    # Terapkan fungsi get_fmea_severity ke setiap baris
    filtered['FMEA_Severity'] = filtered.apply(
        lambda row: get_fmea_severity(row['Scrab Description'], row['Break Time Description']),
        axis=1
    )
    
    # Pastikan tipe numerik
    filtered['FMEA_Severity'] = pd.to_numeric(filtered['FMEA_Severity'], errors='coerce')
    
    # Statistik FMEA Severity
    print(f"     ✓ FMEA Severity Score berhasil dihitung")
    print(f"     ✓ Range severity: {filtered['FMEA_Severity'].min():.0f} - {filtered['FMEA_Severity'].max():.0f}")
    print(f"     ✓ Rata-rata severity: {filtered['FMEA_Severity'].mean():.2f}")
    print(f"     ✓ Median severity: {filtered['FMEA_Severity'].median():.0f}")
    
    # Distribusi severity
    print(f"\n     Distribusi FMEA Severity:")
    severity_counts = filtered['FMEA_Severity'].value_counts().sort_index()
    for sev, count in severity_counts.head(10).items():
        percentage = (count / len(filtered)) * 100
        print(f"       Severity {int(sev)}: {count} kejadian ({percentage:.1f}%)")
    
    # ========================================================================
    # FEATURE ENGINEERING: One-Hot Encoding Fitur Kategorikal (Fishbone + Shift)
    # ========================================================================
    print("\n  → Melakukan one-hot encoding fitur kategorikal (Fishbone Analysis + Shift)...")
    
    # Kolom teks yang akan di-encode (TAMBAHKAN 'Shift')
    text_features = ['Scrab Description', 'Break Time Description', 'Shift']
    
    # Ganti nilai NaN dengan '_NONE_' agar bisa diproses
    for col in text_features:
        if col in filtered.columns:
            filtered[col] = filtered[col].fillna('_NONE_')
            # Normalisasi: uppercase dan strip whitespace (kecuali Shift yang berupa angka)
            if col == 'Shift':
                # Shift biasanya angka (1, 2, 3), konversi ke string
                filtered[col] = filtered[col].astype(str).str.strip()
            else:
                filtered[col] = filtered[col].astype(str).str.strip().str.upper()
        else:
            print(f"     ⚠ Kolom '{col}' tidak ditemukan, dilewati.")
    
    # Lakukan one-hot encoding
    # drop_first=False agar kita dapat semua kategori (penting untuk interpretasi)
    filtered_encoded = pd.get_dummies(
        filtered, 
        columns=[col for col in text_features if col in filtered.columns],
        prefix=text_features,
        drop_first=False,
        dtype=int
    )
    
    # Hitung jumlah fitur dummy yang dibuat
    original_cols = set(filtered.columns)
    new_cols = set(filtered_encoded.columns)
    dummy_cols = new_cols - original_cols
    
    print(f"     ✓ Jumlah fitur dummy kategorikal: {len(dummy_cols)}")
    print(f"     ✓ Total fitur setelah encoding: {len(filtered_encoded.columns)}")
    
    # Tampilkan beberapa contoh fitur dummy yang dibuat
    if len(dummy_cols) > 0:
        sample_dummies = list(dummy_cols)[:5]
        print(f"     ✓ Contoh fitur dummy: {sample_dummies}")
    
    return filtered_encoded


def train_and_save_model(df: pd.DataFrame, model_path: Path = Path("model.pkl")):
    """
    Latih model RandomForestRegressor dengan evaluasi menggunakan train-test split,
    kemudian latih ulang dengan seluruh data dan simpan.
    Menggunakan SEMUA FITUR hasil feature engineering (OEE + Kategorikal).
    """
    # ========================================================================
    # PERSIAPAN FITUR DAN TARGET
    # ========================================================================
    print("\n" + "="*70)
    print("PERSIAPAN DATA UNTUK TRAINING")
    print("="*70)
    
    # Target (y): Waktu Downtime
    y = df["Waktu Downtime (Menit)"]
    
    # Fitur (X): Fitur kategorikal "Fishbone + Shift" + FMEA Severity (alasan + konteks + keparahan)
    # Model "Fishbone + Shift + FMEA" - Menghapus SEMUA fitur produksi untuk mencegah kebocoran data
    features_to_drop = [
        'Waktu Downtime (Menit)',   # Target variable
        'Work Center',               # Sudah difilter, tidak informatif
        'Scrab Description',         # Sudah di-encode menjadi Scrab Description_*
        'Break Time Description',    # Sudah di-encode menjadi Break Time Description_*
        'Shift',                     # Sudah di-encode menjadi Shift_1.0, Shift_2.0, dll
        
        # === HAPUS FITUR PRODUKSI (Data Leakage Prevention) ===
        'Total Produksi (Pcs)',      # Bisa menyebabkan korelasi palsu
        'Produk Cacat (Pcs)',        # Bisa menyebabkan korelasi palsu
        'Quality_Rate',              # Dihitung dari produksi (kebocoran data)
        'Availability_Rate',         # Dihitung dari target variable (kebocoran data)
        
        # Kolom non-numerik lainnya yang harus dibuang
        'Posting Date',
        'Machine',
        'Group', 
        'Shift',
        'Prod Order',
        'Confirm KG',
        'Act Confirm KG',
        'Scrab KG',
        'Start.Date',
        'Start.Time',
        'Finis.Time',
        'Finis.Date'
    ]
    
    # PENTING: FMEA_Severity TIDAK ada di features_to_drop
    # Ini adalah fitur input valid yang memberikan konteks keparahan
    
    # Drop kolom yang tidak diperlukan (jika ada)
    cols_to_drop = [col for col in features_to_drop if col in df.columns]
    X = df.drop(columns=cols_to_drop)
    
    # PENTING: Pastikan semua kolom di X adalah numerik
    # Filter hanya kolom dengan tipe numerik (int, float) atau boolean (hasil one-hot encoding)
    numeric_cols = X.select_dtypes(include=[np.number]).columns
    X = X[numeric_cols]
    
    # Tampilkan informasi fitur
    print(f"\nJumlah sampel data: {len(X)}")
    print(f"Jumlah fitur: {len(X.columns)}")
    print(f"\nFitur yang digunakan ({len(X.columns)} fitur):")
    
    # Kategorikan fitur untuk tampilan yang lebih rapi
    base_features = [col for col in X.columns if not any(
        col.startswith(prefix) for prefix in ['Scrab Description_', 'Break Time Description_', 'Shift_']
    )]
    scrab_features = [col for col in X.columns if col.startswith('Scrab Description_')]
    break_features = [col for col in X.columns if col.startswith('Break Time Description_')]
    shift_features = [col for col in X.columns if col.startswith('Shift_')]
    
    print(f"\n  A. Fitur Numerik Dasar ({len(base_features)} fitur):")
    if len(base_features) > 0:
        for feat in base_features:
            print(f"     - {feat}")
    else:
        print(f"     ⚠ TIDAK ADA (Model Murni Fishbone)")
    
    print(f"\n  B. Fitur Kategorikal 'Scrab Description' ({len(scrab_features)} fitur):")
    if len(scrab_features) <= 10:
        for feat in scrab_features:
            print(f"     - {feat}")
    else:
        for feat in scrab_features[:5]:
            print(f"     - {feat}")
        print(f"     ... dan {len(scrab_features) - 5} fitur lainnya")
    
    print(f"\n  C. Fitur Kategorikal 'Break Time Description' ({len(break_features)} fitur):")
    if len(break_features) <= 10:
        for feat in break_features:
            print(f"     - {feat}")
    else:
        for feat in break_features[:5]:
            print(f"     - {feat}")
        print(f"     ... dan {len(break_features) - 5} fitur lainnya")
    
    print(f"\n  D. Fitur Kategorikal 'Shift' ({len(shift_features)} fitur):")
    for feat in shift_features:
        print(f"     - {feat}")
    
    # ========================================================================
    # TAHAP EVALUASI MODEL (Train-Test Split)
    # ========================================================================
    print("\n" + "="*70)
    print("TAHAP EVALUASI MODEL (Train-Test Split 80:20)")
    print("="*70)
    
    # Split data: 80% training, 20% testing
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    print(f"\nJumlah data training: {len(X_train)} baris ({len(X_train)/len(X)*100:.1f}%)")
    print(f"Jumlah data testing: {len(X_test)} baris ({len(X_test)/len(X)*100:.1f}%)")
    
    # Latih model pada data training
    print("\nMelatih model pada data training...")
    model_eval = RandomForestRegressor(
        n_estimators=100, 
        random_state=42,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        n_jobs=-1  # Gunakan semua CPU cores
    )
    model_eval.fit(X_train, y_train)
    
    # Prediksi pada data testing
    print("Melakukan prediksi pada data testing...")
    y_pred = model_eval.predict(X_test)
    
    # Hitung metrik evaluasi
    mae = mean_absolute_error(y_test, y_pred)
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    
    # Hitung MAPE (Mean Absolute Percentage Error)
    # Hindari pembagian dengan nol
    mape = np.mean(np.abs((y_test - y_pred) / np.where(y_test != 0, y_test, 1))) * 100
    
    # Hitung R² Score untuk mengukur goodness of fit
    r2_score = model_eval.score(X_test, y_test)
    
    # Tampilkan hasil evaluasi
    print("\n" + "-"*70)
    print("HASIL EVALUASI MODEL")
    print("-"*70)
    print(f"MAE (Mean Absolute Error)       : {mae:.4f} menit")
    print(f"RMSE (Root Mean Squared Error)  : {rmse:.4f} menit")
    print(f"MAPE (Mean Absolute % Error)    : {mape:.4f}%")
    print(f"R² Score                        : {r2_score:.4f}")
    print("-"*70)
    
    # Interpretasi hasil
    print(f"\nInterpretasi Hasil:")
    if mae < 10:
        print(f"  ✓ EXCELLENT: MAE < 10 menit (Model sangat akurat)")
    elif mae < 20:
        print(f"  ✓ GOOD: MAE < 20 menit (Model akurat)")
    elif mae < 30:
        print(f"  ⚠ FAIR: MAE < 30 menit (Model cukup akurat)")
    else:
        print(f"  ✗ POOR: MAE ≥ 30 menit (Model perlu perbaikan)")
    
    if r2_score > 0.9:
        print(f"  ✓ EXCELLENT: R² > 0.9 (Model menjelaskan >90% variasi data)")
    elif r2_score > 0.7:
        print(f"  ✓ GOOD: R² > 0.7 (Model menjelaskan >70% variasi data)")
    elif r2_score > 0.5:
        print(f"  ⚠ FAIR: R² > 0.5 (Model menjelaskan >50% variasi data)")
    else:
        print(f"  ✗ POOR: R² ≤ 0.5 (Model kurang baik)")
    
    # Informasi feature importance (top 10)
    print(f"\n" + "-"*70)
    print(f"TOP 10 FEATURE IMPORTANCE")
    print("-"*70)
    feature_importance = pd.DataFrame({
        'feature': X.columns,
        'importance': model_eval.feature_importances_
    }).sort_values('importance', ascending=False)
    
    for idx, row in feature_importance.head(10).iterrows():
        print(f"  {row['importance']:.4f} - {row['feature']}")
    
    # ========================================================================
    # TAHAP TRAINING FINAL (Menggunakan 100% Data)
    # ========================================================================
    print("\n" + "="*70)
    print("TAHAP TRAINING FINAL (Menggunakan 100% Data)")
    print("="*70)
    
    # Latih ulang model dengan SELURUH data (100%)
    print(f"\nMelatih ulang model dengan seluruh data ({len(X)} baris)...")
    model_final = RandomForestRegressor(
        n_estimators=100, 
        random_state=42,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        n_jobs=-1
    )
    model_final.fit(X, y)
    
    # Simpan model final
    joblib.dump(model_final, model_path)
    print(f"\n✓ Model final berhasil dilatih dan disimpan ke '{model_path.name}'")
    print(f"  Jumlah data training final: {len(X)} baris (100%)")
    print(f"  Jumlah fitur: {len(X.columns)}")
    
    # Simpan juga daftar fitur untuk referensi
    feature_names_path = model_path.parent / "feature_names.pkl"
    joblib.dump(list(X.columns), feature_names_path)
    print(f"\n✓ Daftar nama fitur disimpan ke '{feature_names_path.name}'")
    
    # Simpan feature importance dari model final
    feature_importance_final = pd.DataFrame({
        'feature': X.columns,
        'importance': model_final.feature_importances_
    }).sort_values('importance', ascending=False)
    
    feature_importance_path = model_path.parent / "feature_importance.csv"
    feature_importance_final.to_csv(feature_importance_path, index=False)
    print(f"✓ Feature importance disimpan ke '{feature_importance_path.name}'")
    
    print("\n" + "="*70)
    print("RINGKASAN METRIK EVALUASI (untuk dokumentasi skripsi)")
    print("="*70)
    print(f"MAE   : {mae:.4f} menit")
    print(f"RMSE  : {rmse:.4f} menit")
    print(f"MAPE  : {mape:.4f}%")
    print(f"R²    : {r2_score:.4f}")
    print(f"Fitur : {len(X.columns)} fitur (Fishbone + Shift + FMEA Severity)")
    print("="*70)


def main():
    """Fungsi utama untuk menjalankan seluruh proses."""
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir.parent / "Data Flexo CSV"
    model_output_path = base_dir / "model.pkl"

    try:
        print("Mulai proses training model...\n")
        print("💡 Model 'Fishbone + Shift + FMEA' - Menambahkan skor keparahan ke prediksi")
        print("Memuat file CSV (urutan: September 2024 - September 2025):")
        combined_df, file_count = load_and_concat_csv(data_dir)
        print(f"\n✓ Berhasil memuat dan menggabungkan {file_count} file CSV.")
        print(f"  Total baris data: {len(combined_df)}")
        
        print(f"\nMemfilter data untuk Work Center C_FL104...")
        processed_df = preprocess_for_machine(combined_df, work_center="C_FL104")
        print(f"✓ Data untuk C_FL104 ditemukan: {len(processed_df)} baris.")
        
        print(f"\nMelatih model RandomForestRegressor dengan fitur Fishbone + Shift + FMEA Severity...")
        train_and_save_model(processed_df, model_path=model_output_path)
        print(f"\n✓ Model untuk C_FL104 berhasil dilatih dari {file_count} file dan disimpan sebagai model.pkl")
        print(f"✓ Fitur FMEA Severity Score berhasil ditambahkan (skor keparahan 1-10)")
        print(f"✓ Model sekarang memahami tingkat keparahan setiap jenis downtime")
        
    except Exception as e:
        print(f"\n✗ Error: Gagal melatih model. Pesan: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
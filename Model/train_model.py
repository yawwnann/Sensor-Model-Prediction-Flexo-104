import sys
from pathlib import Path
import glob
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.preprocessing import MultiLabelBinarizer
import joblib
from datetime import datetime
import re
from difflib import SequenceMatcher

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


def normalize_text(text: str) -> str:
    """
    Normalisasi teks untuk pencocokan:
    - Uppercase
    - Hapus spasi ekstra
    - Hapus karakter non-alfanumerik (kecuali spasi)
    """
    if pd.isna(text) or text == '':
        return ''
    text = str(text).upper().strip()
    text = re.sub(r'[^\w\s]', ' ', text)  # Hapus tanda baca
    text = re.sub(r'\s+', ' ', text)  # Hapus spasi ganda
    return text


def similarity_score(text1: str, text2: str) -> float:
    """
    Hitung similarity score antara dua teks (0.0 - 1.0).
    Menggunakan SequenceMatcher untuk perbandingan string.
    """
    if not text1 or not text2:
        return 0.0
    return SequenceMatcher(None, text1, text2).ratio()


def clean_technician_names(tech_string: str) -> list:
    """
    Bersihkan dan parse nama teknisi dari string.
    Input bisa berisi multiple names separated by newlines.
    
    Args:
        tech_string: String berisi nama teknisi (mungkin dengan \\n)
        
    Returns:
        List nama teknisi yang sudah dibersihkan
    """
    if pd.isna(tech_string) or tech_string == '':
        return []
    
    # Split by newline and clean each name
    names = str(tech_string).split('\n')
    cleaned_names = []
    
    for name in names:
        name = name.strip().upper()
        if name and name not in ['', 'NAN', 'NONE']:
            cleaned_names.append(name)
    
    return cleaned_names


def load_repair_history(repair_file_path: Path) -> pd.DataFrame:
    """
    Memuat data riwayat perbaikan dari CSV.
    
    Args:
        repair_file_path: Path ke file RIWAYAT_PERBAIKAN.csv
        
    Returns:
        DataFrame dengan kolom Date, ISSUE, ACTION PLAN, EKSEKUTOR, dll
    """
    try:
        df = pd.read_csv(repair_file_path, sep=';', encoding='utf-8-sig')
        
        # Convert Date to datetime (handle both 'Date' and 'TANGGAL' columns)
        date_col = 'TANGGAL' if 'TANGGAL' in df.columns else 'Date'
        df['Date'] = pd.to_datetime(df[date_col], format='%d/%m/%Y', errors='coerce')
        
        # Filter hanya FLEXO 104 (if column exists)
        if 'ITEM UNIT' in df.columns:
            df = df[df['ITEM UNIT'] == 'FLEXO 104'].copy()
        
        # Normalize ISSUE text untuk matching
        df['ISSUE_NORMALIZED'] = df['ISSUE'].apply(normalize_text)
        
        # Clean technician names (handle both 'EKSEKUTOR' and 'TEKNISI' columns)
        teknisi_col = 'TEKNISI' if 'TEKNISI' in df.columns else 'EKSEKUTOR'
        df['TEKNISI_LIST'] = df[teknisi_col].apply(clean_technician_names)
        
        # Clean ACTION PLAN text (handle both 'ACTION PLAN' and 'ACTION_PLAN' columns)
        action_col = 'ACTION_PLAN' if 'ACTION_PLAN' in df.columns else 'ACTION PLAN'
        df['ACTION_PLAN_CLEANED'] = df[action_col].apply(
            lambda x: normalize_text(x) if pd.notna(x) else ''
        )
        
        # Create binary feature: Ada Spare Part (from SPARE_PART column or ACTION_PLAN text)
        if 'SPARE_PART' in df.columns:
            df['HAS_SPARE_PART'] = df['SPARE_PART'].apply(lambda x: 1 if str(x).upper() == 'YA' else 0)
        else:
            spare_part_keywords = ['GANTI', 'SPARE', 'PART', 'SPAREPART', 'PENGGANTIAN']
            df['HAS_SPARE_PART'] = df['ACTION_PLAN_CLEANED'].apply(
                lambda x: 1 if any(keyword in x for keyword in spare_part_keywords) else 0
            )
        
        print(f"\n✓ Data riwayat perbaikan dimuat: {len(df)} kejadian")
        print(f"  Periode: {df['Date'].min()} s/d {df['Date'].max()}")
        
        # Show technician distribution
        all_techs = []
        for tech_list in df['TEKNISI_LIST']:
            all_techs.extend(tech_list)
        unique_techs = set(all_techs)
        print(f"  Jumlah teknisi unik: {len(unique_techs)}")
        print(f"  Teknisi: {', '.join(sorted(unique_techs)[:10])}{'...' if len(unique_techs) > 10 else ''}")
        
        return df
        
    except Exception as e:
        print(f"\n✗ Error memuat riwayat perbaikan: {e}")
        raise


def merge_production_with_repairs(production_df: pd.DataFrame, repair_df: pd.DataFrame) -> pd.DataFrame:
    """
    Menggabungkan data produksi/downtime dengan data riwayat perbaikan.
    
    Strategi:
    1. Match berdasarkan Date (tanggal yang sama)
    2. Match berdasarkan similarity deskripsi masalah
    3. Ambil match terbaik (highest similarity score)
    
    Args:
        production_df: DataFrame data produksi/downtime
        repair_df: DataFrame riwayat perbaikan
        
    Returns:
        DataFrame yang sudah di-merge dengan kolom repair tambahan
    """
    print("\n" + "="*70)
    print("MERGING DATA PRODUKSI DENGAN RIWAYAT PERBAIKAN")
    print("="*70)
    
    # Create Date column from Posting Date in production data
    # Try multiple date formats (YYYY-MM-DD is ISO format from CSV)
    production_df = production_df.copy()
    
    if 'Posting Date' in production_df.columns:
        # First try ISO format (YYYY-MM-DD) which is common in exports
        production_df['Date'] = pd.to_datetime(
            production_df['Posting Date'], 
            format='%Y-%m-%d', 
            errors='coerce'
        )
        
        # If that failed, try DD/MM/YYYY
        if production_df['Date'].isna().all():
            production_df['Date'] = pd.to_datetime(
                production_df['Posting Date'], 
                format='%d/%m/%Y', 
                errors='coerce'
            )
    elif 'Start.Date' in production_df.columns:
        production_df['Date'] = pd.to_datetime(
            production_df['Start.Date'], 
            format='%Y-%m-%d', 
            errors='coerce'
        )
        if production_df['Date'].isna().all():
            production_df['Date'] = pd.to_datetime(
                production_df['Start.Date'], 
                format='%d/%m/%Y', 
                errors='coerce'
            )
    else:
        raise ValueError("Tidak ditemukan kolom tanggal (Posting Date atau Start.Date)")
    
    # Extract just the date (without time) for matching
    production_df['Date'] = production_df['Date'].dt.date
    
    print(f"  ✓ Kolom Date dibuat dari production data")
    
    # Get date range safely
    valid_prod_dates = production_df['Date'].dropna()
    if len(valid_prod_dates) > 0:
        print(f"  ✓ Range tanggal produksi: {valid_prod_dates.min()} s/d {valid_prod_dates.max()}")
    else:
        raise ValueError("Tidak ada tanggal valid di production data!")
    
    # Normalize issue descriptions in production data
    production_df['ISSUE_NORMALIZED_PROD'] = production_df.apply(
        lambda row: normalize_text(
            str(row.get('Scrab Description', '')) + ' ' + 
            str(row.get('Break Time Description', ''))
        ),
        axis=1
    )
    
    # Prepare repair data for merge
    repair_merge_cols = [
        'Date', 'ISSUE', 'ISSUE_NORMALIZED', 'ACTION_PLAN_CLEANED', 
        'TEKNISI_LIST', 'HAS_SPARE_PART'
    ]
    repair_for_merge = repair_df[repair_merge_cols].copy()
    
    # Convert repair Date to date only (no time)
    repair_for_merge['Date'] = pd.to_datetime(repair_for_merge['Date']).dt.date
    
    # Show repair date range
    print(f"  ✓ Repair data date range: {repair_for_merge['Date'].min()} s/d {repair_for_merge['Date'].max()}")
    
    # Find overlapping dates
    prod_dates = set(production_df['Date'].dropna())
    repair_dates = set(repair_for_merge['Date'].dropna())
    overlap_dates = prod_dates & repair_dates
    
    print(f"  ✓ Production unique dates: {len(prod_dates)}")
    print(f"  ✓ Repair unique dates: {len(repair_dates)}")
    print(f"  ✓ Overlapping dates: {len(overlap_dates)}")
    
    if len(overlap_dates) > 0:
        print(f"  ✓ Contoh tanggal yang overlap: {sorted(list(overlap_dates))[:5]}")
    else:
        print(f"  ⚠ PERINGATAN: Tidak ada tanggal yang overlap!")
        print(f"  ⚠ Ini berarti data repair tidak akan ter-merge dengan production data")
    
    # Merge by Date (left join to keep all production data)
    print(f"\n→ Step 1: Merge berdasarkan Date...")
    merged = production_df.merge(
        repair_for_merge,
        on='Date',
        how='left',
        suffixes=('', '_REPAIR')
    )
    
    print(f"  ✓ Total rows after date merge: {len(merged)}")
    
    # For rows with multiple repair matches on same date, pick best match based on text similarity
    print(f"\n→ Step 2: Mencocokkan berdasarkan similarity deskripsi...")
    
    def find_best_repair_match(group):
        """Find best matching repair record for this production record"""
        if len(group) == 1:
            return group.iloc[0]
        
        # Calculate similarity scores
        prod_issue = group.iloc[0]['ISSUE_NORMALIZED_PROD']
        best_idx = 0
        best_score = 0.0
        
        for idx, row in group.iterrows():
            repair_issue = row['ISSUE_NORMALIZED']
            if pd.notna(repair_issue):
                score = similarity_score(prod_issue, repair_issue)
                if score > best_score:
                    best_score = score
                    best_idx = group.index.get_loc(idx)
        
        return group.iloc[best_idx]
    
    # Group by original production row index and pick best match
    # (This handles duplicate rows created by merge when multiple repairs on same date)
    original_indices = production_df.index
    merged['ORIGINAL_IDX'] = merged.index % len(production_df)
    
    # Keep only best match for each production row
    merged_best = merged.groupby('ORIGINAL_IDX', group_keys=False).apply(find_best_repair_match)
    merged_best = merged_best.drop(columns=['ORIGINAL_IDX'])
    
    # Count successful matches
    matched_count = merged_best['ISSUE'].notna().sum()
    match_rate = (matched_count / len(merged_best)) * 100
    
    print(f"  ✓ Berhasil match: {matched_count}/{len(merged_best)} baris ({match_rate:.1f}%)")
    print(f"  ✓ Rows dengan data repair: {matched_count}")
    print(f"  ✓ Rows tanpa data repair: {len(merged_best) - matched_count}")
    
    # Fill missing repair data with defaults
    print(f"\n→ Step 3: Mengisi nilai default untuk rows tanpa match...")
    
    # For rows without repair match, set default values
    merged_best['TEKNISI_LIST'] = merged_best['TEKNISI_LIST'].apply(
        lambda x: x if isinstance(x, list) else []
    )
    merged_best['HAS_SPARE_PART'] = merged_best['HAS_SPARE_PART'].fillna(0).astype(int)
    merged_best['ACTION_PLAN_CLEANED'] = merged_best['ACTION_PLAN_CLEANED'].fillna('UNKNOWN')
    
    print(f"  ✓ Nilai default diterapkan")
    print("="*70)
    
    return merged_best


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
    4. FMEA Severity scoring
    5. **[BARU]** Teknisi encoding (MultiLabelBinarizer)
    6. **[BARU]** Action Plan encoding (One-hot atau TF-IDF)
    7. **[BARU]** Spare Part feature (binary)
    
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
    # FEATURE ENGINEERING BARU: TEKNISI (MultiLabelBinarizer)
    # ========================================================================
    print("\n  → Encoding fitur TEKNISI (dari riwayat perbaikan)...")
    
    if 'TEKNISI_LIST' in filtered.columns:
        # MultiLabelBinarizer untuk multiple technicians per incident
        mlb = MultiLabelBinarizer()
        teknisi_encoded = mlb.fit_transform(filtered['TEKNISI_LIST'])
        
        # Create DataFrame with technician columns
        teknisi_cols = [f'TEKNISI_{name}' for name in mlb.classes_]
        teknisi_df = pd.DataFrame(
            teknisi_encoded, 
            columns=teknisi_cols,
            index=filtered.index
        )
        
        # Merge with main dataframe
        filtered = pd.concat([filtered, teknisi_df], axis=1)
        
        print(f"     ✓ Jumlah teknisi unik: {len(mlb.classes_)}")
        print(f"     ✓ Fitur teknisi dibuat: {len(teknisi_cols)} kolom")
        if len(mlb.classes_) > 0:
            print(f"     ✓ Contoh teknisi: {', '.join(list(mlb.classes_)[:5])}")
        
        # Count rows with technician data
        rows_with_tech = (filtered[teknisi_cols].sum(axis=1) > 0).sum()
        tech_coverage = (rows_with_tech / len(filtered)) * 100
        print(f"     ✓ Rows dengan data teknisi: {rows_with_tech}/{len(filtered)} ({tech_coverage:.1f}%)")
    else:
        print(f"     ⚠ Kolom TEKNISI_LIST tidak ditemukan (skip technician encoding)")
    
    # ========================================================================
    # FEATURE ENGINEERING BARU: ACTION PLAN (One-Hot Encoding)
    # ========================================================================
    print("\n  → Encoding fitur ACTION PLAN...")
    
    if 'ACTION_PLAN_CLEANED' in filtered.columns:
        # Get top N most common action plans (to limit feature explosion)
        TOP_N_ACTIONS = 20
        
        # Count action plan frequencies
        action_counts = filtered['ACTION_PLAN_CLEANED'].value_counts()
        top_actions = action_counts.head(TOP_N_ACTIONS).index.tolist()
        
        # Create binary columns for top actions
        for action in top_actions:
            if action and action != 'UNKNOWN':
                # Create safe column name
                col_name = f'ACTION_{action[:30]}'.replace(' ', '_')
                filtered[col_name] = (filtered['ACTION_PLAN_CLEANED'] == action).astype(int)
        
        action_feature_count = len([col for col in filtered.columns if col.startswith('ACTION_')])
        print(f"     ✓ Top {TOP_N_ACTIONS} action plans digunakan")
        print(f"     ✓ Fitur action plan dibuat: {action_feature_count} kolom")
        
        # Show coverage
        rows_with_action = (filtered['ACTION_PLAN_CLEANED'] != 'UNKNOWN').sum()
        action_coverage = (rows_with_action / len(filtered)) * 100
        print(f"     ✓ Rows dengan action plan: {rows_with_action}/{len(filtered)} ({action_coverage:.1f}%)")
        
        # Show top 5 actions
        if len(top_actions) > 0:
            print(f"     ✓ Top 5 actions:")
            for i, action in enumerate(top_actions[:5], 1):
                count = action_counts[action]
                print(f"        {i}. {action[:50]}... ({count} kejadian)")
    else:
        print(f"     ⚠ Kolom ACTION_PLAN_CLEANED tidak ditemukan (skip action encoding)")
    
    # ========================================================================
    # FEATURE ENGINEERING BARU: SPARE PART (Binary Feature)
    # ========================================================================
    print("\n  → Menambahkan fitur SPARE PART...")
    
    if 'HAS_SPARE_PART' in filtered.columns:
        # Ensure it's integer type
        filtered['HAS_SPARE_PART'] = filtered['HAS_SPARE_PART'].fillna(0).astype(int)
        
        spare_part_count = filtered['HAS_SPARE_PART'].sum()
        spare_part_pct = (spare_part_count / len(filtered)) * 100
        
        print(f"     ✓ Fitur HAS_SPARE_PART ditambahkan")
        print(f"     ✓ Kejadian dengan spare part: {spare_part_count}/{len(filtered)} ({spare_part_pct:.1f}%)")
    else:
        # Create dummy column if not exists
        filtered['HAS_SPARE_PART'] = 0
        print(f"     ⚠ Kolom HAS_SPARE_PART tidak ditemukan, menggunakan nilai default 0")
    
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
    
    # Fitur (X): Fitur kategorikal "Fishbone + Shift" + FMEA Severity + TEKNISI + ACTION PLAN
    # Model "Enhanced" - Menghapus SEMUA fitur produksi untuk mencegah kebocoran data
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
        
        # === KOLOM DARI RIWAYAT PERBAIKAN (raw data, sudah di-encode) ===
        'Date',                      # Tanggal (sudah digunakan untuk merge)
        'ISSUE',                     # Raw issue text (sudah dinormalisasi)
        'ISSUE_NORMALIZED',          # Normalized issue (untuk matching)
        'ISSUE_NORMALIZED_PROD',     # Normalized production issue
        'ACTION PLAN',               # Raw action plan (sudah di-encode)
        'ACTION_PLAN_CLEANED',       # Cleaned action plan (sudah di-encode)
        'TEKNISI_LIST',              # List teknisi (sudah di-encode dengan MLB)
        'EKSEKUTOR',                 # Raw executor names
        'PELAKSANA PERBAIKAN',       # Raw technician names
        'REMARK',                    # Remark text (tidak informatif)
        'ITEM UNIT',                 # Already filtered to FLEXO 104
        'IMPACT',                    # Impact text (redundant with severity)
        
        # Kolom non-numerik lainnya yang harus dibuang
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
        col.startswith(prefix) for prefix in [
            'Scrab Description_', 'Break Time Description_', 'Shift_',
            'TEKNISI_', 'ACTION_'
        ]
    )]
    scrab_features = [col for col in X.columns if col.startswith('Scrab Description_')]
    break_features = [col for col in X.columns if col.startswith('Break Time Description_')]
    shift_features = [col for col in X.columns if col.startswith('Shift_')]
    teknisi_features = [col for col in X.columns if col.startswith('TEKNISI_')]
    action_features = [col for col in X.columns if col.startswith('ACTION_')]
    
    print(f"\n  A. Fitur Numerik Dasar ({len(base_features)} fitur):")
    if len(base_features) > 0:
        for feat in base_features:
            print(f"     - {feat}")
    else:
        print(f"     ⚠ TIDAK ADA (Model Murni Kategorikal)")
    
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
    
    print(f"\n  E. **[BARU]** Fitur 'TEKNISI' ({len(teknisi_features)} fitur):")
    if len(teknisi_features) == 0:
        print(f"     ⚠ TIDAK ADA (data riwayat perbaikan tidak tersedia)")
    elif len(teknisi_features) <= 10:
        for feat in teknisi_features:
            print(f"     - {feat}")
    else:
        for feat in teknisi_features[:5]:
            print(f"     - {feat}")
        print(f"     ... dan {len(teknisi_features) - 5} teknisi lainnya")
    
    print(f"\n  F. **[BARU]** Fitur 'ACTION PLAN' ({len(action_features)} fitur):")
    if len(action_features) == 0:
        print(f"     ⚠ TIDAK ADA (data riwayat perbaikan tidak tersedia)")
    elif len(action_features) <= 10:
        for feat in action_features:
            print(f"     - {feat}")
    else:
        for feat in action_features[:5]:
            print(f"     - {feat}")
        print(f"     ... dan {len(action_features) - 5} action plan lainnya")
    
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
    print(f"\nKomposisi Fitur ({len(X.columns)} total):")
    print(f"  • Fishbone Analysis: {len(scrab_features) + len(break_features)} fitur")
    print(f"  • Shift: {len(shift_features)} fitur")
    print(f"  • FMEA Severity: {'FMEA_Severity' in X.columns}")
    print(f"  • Teknisi: {len(teknisi_features)} fitur")
    print(f"  • Action Plan: {len(action_features)} fitur")
    print(f"  • Spare Part: {'HAS_SPARE_PART' in X.columns}")
    print("="*70)


def main():
    """Fungsi utama untuk menjalankan seluruh proses."""
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir.parent / "Data Flexo CSV"
    repair_file_path = base_dir / "RIWAYAT_PERBAIKAN_REALISTIC.csv"  # Using realistic synthetic data
    model_output_path = base_dir / "model.pkl"

    try:
        print("="*70)
        print("TRAINING MODEL DENGAN DATA RIWAYAT PERBAIKAN (ENHANCED)")
        print("="*70)
        print("Model Enhanced: Fishbone + Shift + FMEA + Teknisi + Action Plan")
        print("="*70)
        
        # ====================================================================
        # STEP 1: LOAD DATA PRODUKSI BULANAN
        # ====================================================================
        print("\n[STEP 1] Memuat data produksi bulanan...")
        print("Memuat file CSV (urutan: September 2024 - September 2025):")
        combined_df, file_count = load_and_concat_csv(data_dir)
        print(f"\n✓ Berhasil memuat dan menggabungkan {file_count} file CSV.")
        print(f"  Total baris data: {len(combined_df)}")
        
        # ====================================================================
        # STEP 2: LOAD DATA RIWAYAT PERBAIKAN
        # ====================================================================
        print("\n[STEP 2] Memuat data riwayat perbaikan...")
        
        if not repair_file_path.exists():
            print(f"\n⚠ WARNING: File riwayat perbaikan tidak ditemukan di: {repair_file_path}")
            print(f"⚠ Model akan dilatih TANPA fitur teknisi dan action plan")
            print(f"⚠ Untuk hasil optimal, pastikan file RIWAYAT_PERBAIKAN.csv tersedia\n")
            df_merged = combined_df
        else:
            repair_df = load_repair_history(repair_file_path)
            
            # ================================================================
            # STEP 3: MERGE DATA PRODUKSI DENGAN RIWAYAT PERBAIKAN
            # ================================================================
            print("\n[STEP 3] Menggabungkan data produksi dengan riwayat perbaikan...")
            df_merged = merge_production_with_repairs(combined_df, repair_df)
            print(f"\n✓ Data berhasil digabungkan: {len(df_merged)} baris")
        
        # ====================================================================
        # STEP 4: PREPROCESSING DAN FEATURE ENGINEERING
        # ====================================================================
        print("\n[STEP 4] Preprocessing dan Feature Engineering...")
        print(f"Memfilter data untuk Work Center C_FL104...")
        processed_df = preprocess_for_machine(df_merged, work_center="C_FL104")
        print(f"\n✓ Data untuk C_FL104 ditemukan: {len(processed_df)} baris.")
        
        # ====================================================================
        # STEP 5: TRAINING MODEL
        # ====================================================================
        print("\n[STEP 5] Training Model RandomForestRegressor...")
        print(f"Model Enhanced dengan fitur:")
        print(f"  • Fishbone Analysis (Scrab & Break Time Description)")
        print(f"  • Shift Information")
        print(f"  • FMEA Severity Score")
        print(f"  • Teknisi (dari riwayat perbaikan)")
        print(f"  • Action Plan (dari riwayat perbaikan)")
        print(f"  • Spare Part Usage (binary feature)")
        print("")
        
        train_and_save_model(processed_df, model_path=model_output_path)
        
        print("\n" + "="*70)
        print("✓ MODEL TRAINING SELESAI!")
        print("="*70)
        print(f"✓ Model untuk C_FL104 berhasil dilatih dan disimpan sebagai model.pkl")
        print(f"✓ Sumber data: {file_count} file CSV produksi + riwayat perbaikan")
        print(f"✓ Total fitur enhanced tersedia untuk prediksi yang lebih akurat")
        print("="*70)
        
    except Exception as e:
        print(f"\nError: Gagal melatih model. Pesan: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
import sys
from pathlib import Path
import glob
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
import joblib
from datetime import datetime


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


def preprocess_for_machine(df: pd.DataFrame, work_center: str = "C_FL104") -> pd.DataFrame:
    """
    Filter hanya untuk work center tertentu dan bersihkan data.
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

    # Konversi tipe numerik yang diperlukan (coerce agar error menjadi NaN)
    numeric_cols = ["Total Produksi (Pcs)", "Produk Cacat (Pcs)", "Waktu Downtime (Menit)"]
    for c in numeric_cols:
        filtered[c] = pd.to_numeric(filtered[c], errors="coerce")

    # Hapus baris yang datanya tidak valid (kosong) pada kolom-kolom penting
    filtered = filtered.dropna(subset=numeric_cols)
    
    return filtered


def train_and_save_model(df: pd.DataFrame, model_path: Path = Path("model.pkl")):
    """
    Latih model RandomForestRegressor dan simpan.
    """
    # Fitur (X) dan Target (y) sesuai kolom yang tersedia
    X = df[["Total Produksi (Pcs)", "Produk Cacat (Pcs)"]]
    y = df["Waktu Downtime (Menit)"]

    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)

    joblib.dump(model, model_path)
    print(f"\nModel berhasil dilatih.")
    print(f"Jumlah data training: {len(df)} baris")
    print(f"Feature Importance: {dict(zip(['Total Produksi (Pcs)', 'Produk Cacat (Pcs)'], model.feature_importances_))}")


def main():
    """Fungsi utama untuk menjalankan seluruh proses."""
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir.parent / "Data Flexo CSV"
    model_output_path = base_dir / "model.pkl"

    try:
        print("Mulai proses training model...\n")
        print("Memuat file CSV (urutan: September 2024 - September 2025):")
        combined_df, file_count = load_and_concat_csv(data_dir)
        print(f"\n✓ Berhasil memuat dan menggabungkan {file_count} file CSV.")
        print(f"  Total baris data: {len(combined_df)}")
        
        print(f"\nMemfilter data untuk Work Center C_FL104...")
        processed_df = preprocess_for_machine(combined_df, work_center="C_FL104")
        print(f"✓ Data untuk C_FL104 ditemukan: {len(processed_df)} baris.")
        
        print(f"\nMelatih model RandomForestRegressor...")
        train_and_save_model(processed_df, model_path=model_output_path)
        print(f"\n✓ Model untuk C_FL104 berhasil dilatih dari {file_count} file dan disimpan sebagai model.pkl")
        
    except Exception as e:
        print(f"\n✗ Error: Gagal melatih model. Pesan: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
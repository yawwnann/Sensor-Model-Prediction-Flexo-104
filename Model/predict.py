import sys
from pathlib import Path
import joblib
import numpy as np
import pandas as pd


def load_model(model_path: Path):
    """
    Memuat model machine learning dari file pickle.
    
    Parameter:
    - model_path: Path ke file model.pkl
    
    Return:
    - model: Model LinearRegression yang sudah dilatih
    """
    try:
        model = joblib.load(model_path)
        print(f"✓ Model berhasil dimuat dari: {model_path}")
        return model
    except FileNotFoundError:
        print(f"✗ Error: File model tidak ditemukan di {model_path}")
        sys.exit(1)
    except Exception as e:
        print(f"✗ Error saat memuat model: {e}")
        sys.exit(1)


def get_user_input():
    """
    Meminta pengguna untuk memasukkan nilai fitur melalui terminal.
    
    Return:
    - tuple: (total_produksi, produk_cacat) sebagai float
    """
    print("\n" + "="*60)
    print("PREDIKSI DURASI MAINTENANCE - MESIN C_FL104")
    print("="*60)
    print("\nSilakan masukkan nilai fitur untuk prediksi:\n")
    
    # Input Fitur 1: Total Produksi (Pcs)
    while True:
        try:
            total_produksi = float(input("Masukkan Total Produksi (Pcs): "))
            if total_produksi < 0:
                print("⚠ Nilai tidak boleh negatif. Silakan coba lagi.")
                continue
            break
        except ValueError:
            print("⚠ Input tidak valid. Masukkan angka yang benar.")
            continue
    
    # Input Fitur 2: Produk Cacat (Pcs)
    while True:
        try:
            produk_cacat = float(input("Masukkan Produk Cacat (Pcs): "))
            if produk_cacat < 0:
                print("⚠ Nilai tidak boleh negatif. Silakan coba lagi.")
                continue
            break
        except ValueError:
            print("⚠ Input tidak valid. Masukkan angka yang benar.")
            continue
    
    return total_produksi, produk_cacat


def prepare_input_data(total_produksi: float, produk_cacat: float) -> np.ndarray:
    """
    Menyiapkan data input dalam format yang sesuai untuk model.
    
    Parameter:
    - total_produksi: Jumlah produksi baik (Pcs)
    - produk_cacat: Jumlah produk cacat (Pcs)
    
    Return:
    - np.ndarray: Array 2D dengan shape (1, 2) untuk prediksi
    """
    # Buat array dengan shape (1, 2) sesuai format training
    input_data = np.array([[total_produksi, produk_cacat]])
    return input_data


def make_prediction(model, input_data: np.ndarray) -> float:
    """
    Melakukan prediksi menggunakan model yang sudah dimuat.
    
    Parameter:
    - model: Model LinearRegression yang sudah dilatih
    - input_data: Array input dengan shape (1, 2)
    
    Return:
    - float: Hasil prediksi durasi maintenance (dalam menit)
    """
    try:
        prediction = model.predict(input_data)
        return prediction[0]
    except Exception as e:
        print(f"✗ Error saat melakukan prediksi: {e}")
        sys.exit(1)


def display_result(total_produksi: float, produk_cacat: float, prediction: float):
    """
    Menampilkan hasil prediksi dengan format yang jelas dan informatif.
    
    Parameter:
    - total_produksi: Jumlah produksi baik (Pcs)
    - produk_cacat: Jumlah produk cacat (Pcs)
    - prediction: Hasil prediksi durasi maintenance (dalam menit)
    """
    print("\n" + "="*60)
    print("HASIL PREDIKSI")
    print("="*60)
    
    # Tampilkan input yang digunakan
    print("\nData Input:")
    print(f"  • Total Produksi (Pcs)    : {total_produksi:,.0f}")
    print(f"  • Produk Cacat (Pcs)      : {produk_cacat:,.0f}")
    
    # Konversi menit ke jam dan menit
    total_minutes = max(0, prediction)  # Pastikan tidak negatif
    hours = int(total_minutes // 60)
    minutes = int(total_minutes % 60)
    
    # Tampilkan hasil prediksi
    print("\nHasil Prediksi:")
    print(f"  • Durasi Maintenance      : {total_minutes:.2f} menit")
    print(f"  • Durasi Maintenance      : {hours} jam {minutes} menit")
    
    # Interpretasi hasil
    print("\nInterpretasi:")
    if total_minutes < 30:
        status = "Maintenance Cepat (< 30 menit)"
    elif total_minutes < 120:
        status = "Maintenance Normal (30-120 menit)"
    else:
        status = "Maintenance Lama (> 120 menit)"
    print(f"  • Status                  : {status}")
    
    print("\n" + "="*60 + "\n")


def main():
    """
    Fungsi utama untuk menjalankan seluruh proses prediksi.
    """
    # Tentukan path model
    base_dir = Path(__file__).resolve().parent
    model_path = base_dir / "model.pkl"
    
    try:
        # 1. Muat model
        print("\nMemuat model machine learning...")
        model = load_model(model_path)
        
        # 2. Dapatkan input dari pengguna
        total_produksi, produk_cacat = get_user_input()
        
        # 3. Siapkan data input
        input_data = prepare_input_data(total_produksi, produk_cacat)
        
        # 4. Lakukan prediksi
        print("\nMelakukan prediksi...")
        prediction = make_prediction(model, input_data)
        
        # 5. Tampilkan hasil
        display_result(total_produksi, produk_cacat, prediction)
        
    except KeyboardInterrupt:
        print("\n\n✗ Proses dibatalkan oleh pengguna.")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error tidak terduga: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

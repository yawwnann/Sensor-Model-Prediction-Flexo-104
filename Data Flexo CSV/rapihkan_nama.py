import os
import re

def standardize_report_names(directory_path: str):
    """
    Mengubah nama file laporan di folder target ke format standar:
    'Laporan Flexo [Bulan] [Tahun].xlsx'

    Args:
        directory_path: Path ke folder yang berisi file laporan.
    """
    # Daftar bulan dalam Bahasa Indonesia untuk pencocokan
    nama_bulan = [
        "Januari", "Februari", "Maret", "April", "Mei", "Juni",
        "Juli", "Agustus", "September", "Oktober", "November", "Desember"
    ]
    
    # Membuat pola regex untuk menemukan nama bulan diikuti 4 digit tahun
    # Contoh: akan cocok dengan "September 2025", "agustus 2025", dll.
    pattern = re.compile(r"({})\s+(\d{{4}})".format("|".join(nama_bulan)), re.IGNORECASE)

    print(f"Memindai file di folder: '{os.path.abspath(directory_path)}'\n")
    
    renamed_count = 0
    skipped_count = 0

    # Loop melalui setiap item di dalam direktori
    for filename in os.listdir(directory_path):
        # Path lengkap ke file
        old_filepath = os.path.join(directory_path, filename)

        # Hanya proses file, bukan folder
        if os.path.isfile(old_filepath):
            # Cari pola bulan dan tahun di dalam nama file
            match = pattern.search(filename)

            # Jika pola ditemukan
            if match:
                bulan = match.group(1).capitalize() # Ambil bulan dan kapitalisasi huruf depannya
                tahun = match.group(2) # Ambil tahun
                
                # Dapatkan ekstensi file asli (misal: .xlsx, .XLSX)
                extension = os.path.splitext(filename)[1]

                # Buat nama file baru yang standar
                new_filename = f"Laporan Flexo {bulan} {tahun}{extension}"
                new_filepath = os.path.join(directory_path, new_filename)

                # Jika nama baru berbeda dengan nama lama, lakukan rename
                if new_filename != filename:
                    try:
                        os.rename(old_filepath, new_filepath)
                        print(f"✅ Berhasil: '{filename}'  ->  '{new_filename}'")
                        renamed_count += 1
                    except OSError as e:
                        print(f"❌ Error saat mengubah '{filename}': {e}")
                        skipped_count += 1
                else:
                    print(f"👍 Sudah Sesuai: '{filename}'")
                    skipped_count += 1
            else:
                # Jika pola bulan dan tahun tidak ditemukan di nama file
                print(f"⏭️ Dilewati: '{filename}' (pola tidak ditemukan)")
                skipped_count += 1
    
    print(f"\nProses Selesai. {renamed_count} file diubah namanya, {skipped_count} file dilewati.")

if __name__ == "__main__":
    # Script akan berjalan di folder tempat ia disimpan.
    # '.' berarti "folder saat ini".
    target_folder = "." 
    standardize_report_names(target_folder)
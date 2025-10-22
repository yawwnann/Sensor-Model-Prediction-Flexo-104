import os
import sys
from pathlib import Path

try:
    import pandas as pd
except ImportError:
    print("Pandas belum terpasang. Install dengan: pip install pandas openpyxl")
    sys.exit(1)


def convert_xlsx_folder_to_csv(
    source_dir: Path,
    output_dir: Path,
    include_extensions=(".xlsx", ".xlsm", ".XLSX", ".XLSM"),
) -> None:
    """
    Konversi semua file Excel dalam folder source_dir menjadi CSV.
    - Setiap sheet akan diekspor ke file CSV terpisah: <nama_file>__<nama_sheet>.csv
    - Hasil disimpan ke output_dir. Folder akan dibuat jika belum ada.

    Param:
    - source_dir: folder sumber yang berisi file Excel
    - output_dir: folder tujuan untuk menyimpan CSV
    - include_extensions: ekstensi file yang akan diproses
    """
    source_dir = Path(source_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if not source_dir.exists():
        raise FileNotFoundError(f"Folder sumber tidak ditemukan: {source_dir}")

    excel_files = [p for p in source_dir.iterdir() if p.is_file() and p.suffix in include_extensions]

    if not excel_files:
        print(f"Tidak ada file Excel dengan ekstensi {include_extensions} di {source_dir}")
        return

    for excel_path in excel_files:
        try:
            # engine openpyxl untuk xlsx/xlsm
            xls = pd.ExcelFile(excel_path, engine="openpyxl")
        except Exception as e:
            print(f"Gagal membuka {excel_path.name}: {e}")
            continue

        safe_base = excel_path.stem.strip()
        # Bersihkan nama dasar file agar aman untuk nama file output
        safe_base = "".join(ch if ch not in "\\/:*?\"<>|" else "_" for ch in safe_base)

        for sheet_name in xls.sheet_names:
            try:
                df = xls.parse(sheet_name)
                # Opsi: drop semua kolom kosong total
                if not df.empty:
                    df = df.dropna(how="all")
                    # normalisasi kolom: jika header ganda, jadikan string
                    df.columns = [str(c) for c in df.columns]

                # Buat nama file aman untuk sheet
                safe_sheet = sheet_name.strip()
                safe_sheet = "".join(ch if ch not in "\\/:*?\"<>|" else "_" for ch in safe_sheet)

                out_name = f"{safe_base}__{safe_sheet}.csv"
                out_path = output_dir / out_name

                # --- PERUBAHAN DI SINI ---
                # Simpan sebagai CSV dengan UTF-8 dan separator titik koma (;)
                df.to_csv(out_path, index=False, encoding="utf-8-sig", sep=';')
                # -------------------------
                
                print(f"Berhasil: {excel_path.name} - sheet '{sheet_name}' -> {out_path}")
            except Exception as e:
                print(f"Gagal konversi {excel_path.name} - sheet '{sheet_name}': {e}")


if __name__ == "__main__":
    # Default: sumber = ./Data Flexo, output = ./Data Flexo CSV
    base_dir = Path(__file__).resolve().parent
    default_source = base_dir / "Data Flexo"
    default_output = base_dir / "Data Flexo CSV"

    # Argumen opsional: python convert_xlsx_to_csv.py [source_dir] [output_dir]
    args = sys.argv[1:]
    source = Path(args[0]) if len(args) >= 1 else default_source
    output = Path(args[1]) if len(args) >= 2 else default_output

    try:
        convert_xlsx_folder_to_csv(source, output)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
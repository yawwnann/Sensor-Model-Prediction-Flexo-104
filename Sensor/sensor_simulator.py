"""
sensor_simulator.py
Smart Sensor Simulator untuk FlexoTwin - Mesin Flexo 104
Mensimulasikan perilaku mesin berdasarkan data historis selama 1 tahun
HANYA untuk mesin C_FL104
"""

import os
import json
import random
import time
from pathlib import Path
from datetime import datetime
import pandas as pd
import paho.mqtt.client as mqtt


# ============================================================================
# KONFIGURASI
# ============================================================================

# Path ke folder data
DATA_FOLDER = Path(__file__).parent / "../Data Flexo CSV"

# MQTT Configuration
MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "flexotwin/machine/status"
MQTT_CLIENT_ID = "flexotwin-sensor-simulator"

# Machine Configuration
TARGET_MACHINE = "C_FL104"

# Simulation Configuration
SIMULATION_INTERVAL = 5  # Detik
PERFORMANCE_VARIANCE = 5  # ±5%
QUALITY_VARIANCE = 2     # ±2%


# ============================================================================
# GLOBAL VARIABLES
# ============================================================================

# Statistik dari data historis
avg_availability_rate = None
avg_performance_rate = None
avg_quality_rate = None
downtime_probability = None

# MQTT Client
mqtt_client = None


# ============================================================================
# PHASE 1: DATA ANALYSIS & INITIALIZATION
# ============================================================================

def load_and_analyze_data():
    """
    Membaca semua file CSV dari folder Data Flexo CSV, filter untuk C_FL104,
    dan menghitung statistik.
    
    Return:
    - tuple: (avg_availability, avg_performance, avg_quality, downtime_prob)
    """
    
    print("\n" + "="*70)
    print("PHASE 1: DATA ANALYSIS & INITIALIZATION")
    print("="*70)
    
    try:
        # ====================================================================
        # STEP 1: Cari semua file CSV
        # ====================================================================
        print(f"\n[INFO] Membaca data dari folder: {DATA_FOLDER}")
        
        if not DATA_FOLDER.exists():
            raise FileNotFoundError(f"Folder tidak ditemukan: {DATA_FOLDER}")
        
        csv_files = list(DATA_FOLDER.glob("*.csv"))
        
        if not csv_files:
            raise FileNotFoundError(f"Tidak ada file CSV di folder: {DATA_FOLDER}")
        
        print(f"[INFO] Ditemukan {len(csv_files)} file CSV")
        
        # ====================================================================
        # STEP 2: Baca dan gabungkan semua file CSV
        # ====================================================================
        print("\n[INFO] Membaca dan menggabungkan file CSV...")
        
        dataframes = []
        for csv_file in csv_files:
            try:
                df = pd.read_csv(csv_file, encoding='utf-8-sig', delimiter=';')
                dataframes.append(df)
                print(f"  ✓ {csv_file.name} ({len(df)} baris)")
            except Exception as e:
                print(f"  ✗ Error membaca {csv_file.name}: {e}")
                continue
        
        if not dataframes:
            raise ValueError("Tidak ada data yang berhasil dibaca")
        
        # Gabungkan semua DataFrame
        combined_df = pd.concat(dataframes, ignore_index=True)
        print(f"\n[SUCCESS] Total data gabungan: {len(combined_df)} baris")
        
        # ====================================================================
        # STEP 2.5: Filter hanya data C_FL104
        # ====================================================================
        print(f"\n[INFO] Memfilter data untuk mesin {TARGET_MACHINE}...")
        
        # Cek kolom yang mungkin berisi nama mesin
        machine_cols = ['Work Center', 'Machine', 'Mesin', 'machine', 'work_center']
        machine_col = None
        
        for col in machine_cols:
            if col in combined_df.columns:
                machine_col = col
                print(f"  ✓ Kolom mesin ditemukan: '{col}'")
                break
        
        if machine_col:
            # Filter hanya C_FL104
            filtered_df = combined_df[combined_df[machine_col].astype(str).str.strip() == TARGET_MACHINE]
            
            if len(filtered_df) > 0:
                combined_df = filtered_df
                print(f"  ✓ Data {TARGET_MACHINE}: {len(combined_df)} baris")
            else:
                print(f"  [WARNING] Tidak ada data untuk {TARGET_MACHINE}. Menggunakan semua data.")
        else:
            print(f"  [WARNING] Kolom mesin tidak ditemukan. Menggunakan semua data.")
            print(f"  [DEBUG] Kolom yang tersedia: {combined_df.columns.tolist()}")
        
        # ====================================================================
        # STEP 3: Hitung statistik
        # ====================================================================
        print(f"\n[INFO] Menghitung statistik dari data historis ({TARGET_MACHINE})...")
        
        # Inisialisasi nilai default
        avg_availability = 85.0
        avg_performance = 82.0
        avg_quality = 96.0
        
        # Coba hitung dari kolom yang ada
        # Cek berbagai nama kolom yang mungkin
        availability_cols = ['Availability Rate (%)', 'availability_rate', 'Availability', 'availability']
        performance_cols = ['Performance Rate (%)', 'performance_rate', 'Performance', 'performance']
        quality_cols = ['Quality Rate (%)', 'quality_rate', 'Quality', 'quality']
        
        # Hitung Availability Rate
        for col in availability_cols:
            if col in combined_df.columns:
                try:
                    avg_availability = pd.to_numeric(combined_df[col], errors='coerce').mean()
                    if pd.notna(avg_availability):
                        print(f"  ✓ Availability Rate: {avg_availability:.2f}%")
                        break
                except:
                    continue
        
        # Hitung Performance Rate
        for col in performance_cols:
            if col in combined_df.columns:
                try:
                    avg_performance = pd.to_numeric(combined_df[col], errors='coerce').mean()
                    if pd.notna(avg_performance):
                        print(f"  ✓ Performance Rate: {avg_performance:.2f}%")
                        break
                except:
                    continue
        
        # Hitung Quality Rate
        for col in quality_cols:
            if col in combined_df.columns:
                try:
                    avg_quality = pd.to_numeric(combined_df[col], errors='coerce').mean()
                    if pd.notna(avg_quality):
                        print(f"  ✓ Quality Rate: {avg_quality:.2f}%")
                        break
                except:
                    continue
        
        # ====================================================================
        # STEP 4: Hitung probabilitas downtime
        # ====================================================================
        downtime_prob = 1 - (avg_availability / 100)
        
        print(f"\n[STATISTICS for {TARGET_MACHINE}]")
        print(f"  • Average Availability Rate: {avg_availability:.2f}%")
        print(f"  • Average Performance Rate: {avg_performance:.2f}%")
        print(f"  • Average Quality Rate: {avg_quality:.2f}%")
        print(f"  • Downtime Probability: {downtime_prob:.4f} ({downtime_prob*100:.2f}%)")
        
        return avg_availability, avg_performance, avg_quality, downtime_prob
        
    except Exception as e:
        print(f"\n[ERROR] Gagal menganalisis data: {e}")
        print(f"[WARNING] Menggunakan nilai default untuk simulasi")
        
        # Return nilai default jika ada error
        return 85.0, 82.0, 96.0, 0.15


# ============================================================================
# PHASE 2: MQTT CONNECTION & SIMULATION
# ============================================================================

def on_connect(client, userdata, flags, rc):
    """Callback saat MQTT client terhubung"""
    if rc == 0:
        print(f"\n[SUCCESS] Terhubung ke MQTT broker: {MQTT_BROKER}")
    else:
        print(f"\n[ERROR] Gagal terhubung ke MQTT broker. Code: {rc}")


def on_disconnect(client, userdata, rc):
    """Callback saat MQTT client terputus"""
    if rc != 0:
        print(f"\n[WARNING] Koneksi MQTT terputus. Code: {rc}")


def on_publish(client, userdata, mid):
    """Callback saat data berhasil dipublikasikan"""
    pass  # Silent publish


def setup_mqtt_connection():
    """
    Membuat koneksi ke MQTT broker.
    
    Return:
    - mqtt_client: MQTT client instance
    """
    
    print("\n" + "="*70)
    print("PHASE 2: MQTT CONNECTION & SIMULATION")
    print("="*70)
    
    try:
        print(f"\n[INFO] Menghubungkan ke MQTT broker: {MQTT_BROKER}:{MQTT_PORT}")
        
        # Buat MQTT client
        client = mqtt.Client(client_id=MQTT_CLIENT_ID)
        
        # Set callbacks
        client.on_connect = on_connect
        client.on_disconnect = on_disconnect
        client.on_publish = on_publish
        
        # Connect ke broker
        client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
        
        # Start network loop
        client.loop_start()
        
        # Tunggu sampai terhubung
        time.sleep(2)
        
        return client
        
    except Exception as e:
        print(f"\n[ERROR] Gagal setup MQTT connection: {e}")
        return None


def simulate_sensor_data():
    """
    Mensimulasikan data sensor berdasarkan statistik historis C_FL104.
    
    Return:
    - dict: Data sensor yang disimulasikan
    """
    
    # Tentukan status mesin berdasarkan probabilitas downtime
    if random.random() < downtime_probability:
        machine_status = "Downtime"
        performance_rate = 0.0
        quality_rate = 0.0
    else:
        machine_status = "Running"
        
        # Simulasikan performance dengan variance
        variance_perf = random.uniform(-PERFORMANCE_VARIANCE, PERFORMANCE_VARIANCE)
        performance_rate = max(0, min(100, avg_performance_rate + variance_perf))
        
        # Simulasikan quality dengan variance
        variance_qual = random.uniform(-QUALITY_VARIANCE, QUALITY_VARIANCE)
        quality_rate = max(0, min(100, avg_quality_rate + variance_qual))
    
    # Buat payload JSON
    sensor_data = {
        "machine_id": TARGET_MACHINE,
        "machine_status": machine_status,
        "performance_rate": round(performance_rate, 2),
        "quality_rate": round(quality_rate, 2),
        "timestamp": datetime.now().isoformat(),
        "simulator_version": "1.0"
    }
    
    return sensor_data


def publish_sensor_data(client, sensor_data):
    """
    Mempublikasikan data sensor ke MQTT broker.
    
    Parameter:
    - client: MQTT client instance
    - sensor_data: Dictionary berisi data sensor
    """
    
    try:
        # Convert ke JSON
        payload = json.dumps(sensor_data)
        
        # Publish ke MQTT topic
        result = client.publish(MQTT_TOPIC, payload, qos=1)
        
        # Check publish result
        if result.rc == mqtt.MQTT_ERR_SUCCESS:
            status_icon = "✓" if sensor_data["machine_status"] == "Running" else "⚠"
            print(f"{status_icon} [{sensor_data['timestamp']}] "
                  f"Status: {sensor_data['machine_status']:8} | "
                  f"Performance: {sensor_data['performance_rate']:6.2f}% | "
                  f"Quality: {sensor_data['quality_rate']:6.2f}%")
        else:
            print(f"[ERROR] Gagal publish data. Code: {result.rc}")
            
    except Exception as e:
        print(f"[ERROR] Error publishing data: {e}")


def run_simulation():
    """
    Menjalankan simulasi sensor dalam infinite loop.
    """
    
    print(f"\n[INFO] Simulasi dimulai. Interval: {SIMULATION_INTERVAL} detik")
    print(f"[INFO] Topic MQTT: {MQTT_TOPIC}")
    print(f"[INFO] Tekan CTRL+C untuk menghentikan simulasi\n")
    
    print("="*70)
    print("SIMULATION RUNNING")
    print("="*70 + "\n")
    
    try:
        iteration = 0
        while True:
            iteration += 1
            
            # Simulasikan data sensor
            sensor_data = simulate_sensor_data()
            
            # Publish ke MQTT
            if mqtt_client and mqtt_client.is_connected():
                publish_sensor_data(mqtt_client, sensor_data)
            else:
                print(f"[WARNING] MQTT client tidak terhubung. Data tidak terkirim.")
            
            # Tunggu sebelum iterasi berikutnya
            time.sleep(SIMULATION_INTERVAL)
            
    except KeyboardInterrupt:
        print(f"\n\n[INFO] Simulasi dihentikan oleh user")
        print(f"[INFO] Total iterasi: {iteration}")
    except Exception as e:
        print(f"\n[ERROR] Error dalam simulasi: {e}")
    finally:
        # Cleanup
        if mqtt_client:
            mqtt_client.loop_stop()
            mqtt_client.disconnect()
            print("[INFO] MQTT connection closed")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """
    Main function untuk menjalankan sensor simulator.
    """
    
    print("\n" + "="*70)
    print("FlexoTwin Smart Sensor Simulator")
    print(f"Machine: {TARGET_MACHINE}")
    print("="*70)
    
    global avg_availability_rate, avg_performance_rate, avg_quality_rate, downtime_probability, mqtt_client
    
    # ========================================================================
    # PHASE 1: Load dan analyze data
    # ========================================================================
    avg_availability_rate, avg_performance_rate, avg_quality_rate, downtime_probability = load_and_analyze_data()
    
    # ========================================================================
    # PHASE 2: Setup MQTT connection
    # ========================================================================
    mqtt_client = setup_mqtt_connection()
    
    if mqtt_client is None:
        print("\n[ERROR] Gagal setup MQTT connection. Simulasi dibatalkan.")
        return
    
    # ========================================================================
    # PHASE 3: Run simulation
    # ========================================================================
    run_simulation()


if __name__ == "__main__":
    main()

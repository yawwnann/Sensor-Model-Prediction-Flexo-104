"""
mqtt_service.py
Service untuk mengelola koneksi MQTT dan menerima data dari sensor simulator
"""

import paho.mqtt.client as mqtt
import json
import time
from ..utils.logger import get_logger
from .database_service import db_service


# ============================================================================
# LOGGING
# ============================================================================

logger = get_logger(__name__)


# ============================================================================
# MQTT CONFIGURATION
# ============================================================================

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "flexotwin/machine/status"
MQTT_CLIENT_ID = "flexotwin-backend-subscriber"
MQTT_KEEPALIVE = 60


# ============================================================================
# GLOBAL DATA STORAGE (Temporary)
# ============================================================================

# Dictionary untuk menyimpan data sensor terbaru
latest_sensor_data = {
    "machine_id": None,
    "machine_status": None,
    "performance_rate": None,
    "quality_rate": None,
    "cumulative_production": 0,
    "cumulative_defects": 0,
    "timestamp": None,
    "simulator_version": None
}

# List untuk menyimpan history data (max 100 entries)
sensor_data_history = []
MAX_HISTORY = 100


# ============================================================================
# MQTT CALLBACKS
# ============================================================================

def on_connect(client, userdata, flags, rc):
    """
    Callback saat MQTT client terhubung ke broker.
    
    Parameter:
    - client: MQTT client instance
    - userdata: User data
    - flags: Connection flags
    - rc: Return code (0 = success)
    """
    
    if rc == 0:
        logger.info("✓ Successfully connected to MQTT Broker!")
        logger.info(f"  Broker: {MQTT_BROKER}:{MQTT_PORT}")
        
        # Subscribe ke topic
        client.subscribe(MQTT_TOPIC)
        logger.info(f"✓ Subscribed to topic: {MQTT_TOPIC}")
    else:
        logger.error(f"✗ Failed to connect to MQTT Broker, return code {rc}")


def on_disconnect(client, userdata, rc):
    """
    Callback saat MQTT client terputus dari broker.
    
    Parameter:
    - client: MQTT client instance
    - userdata: User data
    - rc: Return code
    """
    
    if rc != 0:
        logger.warning(f"⚠ Unexpected disconnection from MQTT Broker (code: {rc})")
    else:
        logger.info("✓ Disconnected from MQTT Broker")


def on_message(client, userdata, msg):
    """
    Callback saat menerima message dari MQTT topic.
    
    Parameter:
    - client: MQTT client instance
    - userdata: User data
    - msg: MQTT message object
    """
    
    try:
        # Decode payload
        payload = msg.payload.decode('utf-8')
        data = json.loads(payload)
        
        logger.info(f"[MQTT RECEIVED] Topic: {msg.topic}")
        logger.info(f"  Machine: {data.get('machine_id')}")
        logger.info(f"  Status: {data.get('machine_status')}")
        logger.info(f"  Performance: {data.get('performance_rate')}%")
        logger.info(f"  Quality: {data.get('quality_rate')}%")
        logger.info(f"  Cumulative Production: {data.get('cumulative_production', 0)} pcs")
        logger.info(f"  Cumulative Defects: {data.get('cumulative_defects', 0)} pcs")
        
        # Persist to database for real-time computations
        db_service.log_machine_status(data)
        
        # Update latest sensor data (in-memory cache) and history
        update_latest_sensor_data(data)
        add_to_history(data)
        
    except json.JSONDecodeError as e:
        logger.error(f"✗ Error decoding JSON from MQTT message: {e}")
    except Exception as e:
        logger.error(f"✗ Error processing MQTT message: {e}")


def on_subscribe(client, userdata, mid, granted_qos):
    """
    Callback saat subscription berhasil.
    
    Parameter:
    - client: MQTT client instance
    - userdata: User data
    - mid: Message ID
    - granted_qos: Granted QoS level
    """
    
    logger.debug(f"Subscription confirmed with QoS: {granted_qos}")


# ============================================================================
# DATA MANAGEMENT FUNCTIONS
# ============================================================================

def update_latest_sensor_data(data):
    """
    Update data sensor terbaru.
    
    Parameter:
    - data: Dictionary berisi sensor data
    """
    
    global latest_sensor_data
    
    latest_sensor_data = {
        "machine_id": data.get("machine_id"),
        "machine_status": data.get("machine_status"),
        "performance_rate": data.get("performance_rate"),
        "quality_rate": data.get("quality_rate"),
        "cumulative_production": data.get("cumulative_production", 0),
        "cumulative_defects": data.get("cumulative_defects", 0),
        "timestamp": data.get("timestamp"),
        "simulator_version": data.get("simulator_version")
    }


def add_to_history(data):
    """
    Tambahkan data ke history dengan limit maksimal.
    
    Parameter:
    - data: Dictionary berisi sensor data
    """
    
    global sensor_data_history
    
    sensor_data_history.append(data)
    
    # Hapus entry tertua jika sudah mencapai limit
    if len(sensor_data_history) > MAX_HISTORY:
        sensor_data_history.pop(0)


def get_latest_sensor_data():
    """
    Mendapatkan data sensor terbaru.
    
    Return:
    - dict: Latest sensor data
    """
    
    return latest_sensor_data.copy()


def get_sensor_data_history(limit=None):
    """
    Mendapatkan history data sensor.
    
    Parameter:
    - limit: Jumlah data yang ingin diambil (None = semua)
    
    Return:
    - list: List of sensor data
    """
    
    if limit is None:
        return sensor_data_history.copy()
    else:
        return sensor_data_history[-limit:].copy()


def clear_history():
    """
    Menghapus semua history data.
    """
    
    global sensor_data_history
    sensor_data_history = []
    logger.info("Sensor data history cleared")


# ============================================================================
# MQTT CLIENT CLASS
# ============================================================================

class MQTTClient:
    """
    Class untuk mengelola MQTT client connection dan subscription.
    """
    
    def __init__(self):
        """
        Inisialisasi MQTT client.
        """
        
        self.client = mqtt.Client(client_id=MQTT_CLIENT_ID)
        self.client.on_connect = on_connect
        self.client.on_disconnect = on_disconnect
        self.client.on_message = on_message
        self.client.on_subscribe = on_subscribe
        
        self.is_connected = False
        self.is_stopping = False
        logger.debug("MQTT Client initialized")
    
    def start(self):
        """
        Memulai koneksi ke MQTT broker dan menjalankan loop di background thread.
        """
        
        try:
            logger.info(f"[MQTT] Connecting to broker at {MQTT_BROKER}:{MQTT_PORT}...")
            
            # Connect ke broker
            self.client.connect(MQTT_BROKER, MQTT_PORT, MQTT_KEEPALIVE)
            
            # Jalankan network loop di background thread
            self.client.loop_start()
            
            # Tunggu sebentar untuk koneksi establish
            time.sleep(2)
            
            self.is_connected = True
            logger.info("[MQTT] Client started successfully")
            
        except Exception as e:
            logger.error(f"[MQTT] Error starting client: {e}")
            self.is_connected = False
    
    def stop(self):
        """
        Menghentikan koneksi MQTT client.
        """
        
        if self.is_stopping:
            return
            
        self.is_stopping = True
        
        try:
            logger.info("[MQTT] Stopping client...")
            
            # Stop the network loop first
            self.client.loop_stop()
            
            # Then disconnect
            if self.is_connected:
                self.client.disconnect()
            
            # Wait for clean disconnect
            time.sleep(0.3)
            
            self.is_connected = False
            logger.info("[MQTT] Client stopped cleanly")
            
        except Exception as e:
            logger.error(f"[MQTT] Error stopping client: {e}")
            self.is_connected = False
        finally:
            self.is_stopping = False
    
    def is_connected_to_broker(self):
        """
        Mengecek apakah client terhubung ke broker.
        
        Return:
        - bool: True jika terhubung, False jika tidak
        """
        
        return self.is_connected
    
    def publish(self, topic, payload, qos=1):
        """
        Mempublikasikan message ke MQTT topic.
        
        Parameter:
        - topic: MQTT topic
        - payload: Message payload (dict atau string)
        - qos: Quality of Service (0, 1, atau 2)
        
        Return:
        - bool: True jika berhasil, False jika gagal
        """
        
        try:
            if isinstance(payload, dict):
                payload = json.dumps(payload)
            
            result = self.client.publish(topic, payload, qos=qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"[MQTT] Published to {topic}")
                return True
            else:
                logger.error(f"[MQTT] Publish failed with code {result.rc}")
                return False
                
        except Exception as e:
            logger.error(f"[MQTT] Error publishing message: {e}")
            return False


# ============================================================================
# GLOBAL MQTT CLIENT INSTANCE
# ============================================================================

# Instance global yang akan digunakan di seluruh aplikasi
mqtt_client_instance = None


def get_mqtt_client():
    """
    Mendapatkan global MQTT client instance.
    
    Return:
    - MQTTClient: Global MQTT client instance
    """
    
    global mqtt_client_instance
    
    if mqtt_client_instance is None:
        mqtt_client_instance = MQTTClient()
    
    return mqtt_client_instance


def initialize_mqtt():
    """
    Inisialisasi dan jalankan MQTT client.
    """
    
    client = get_mqtt_client()
    client.start()
    return client

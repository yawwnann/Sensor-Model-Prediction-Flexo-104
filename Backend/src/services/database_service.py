"""
Database Service
Layanan untuk operasi database PostgreSQL dengan pattern yang lebih rapi
"""

import psycopg2
from psycopg2 import sql, OperationalError
import socket
import time
from typing import Optional, Tuple, List, Dict, Any
from contextlib import contextmanager

from config import DATABASE_URL, DB_CONNECTION_TIMEOUT, DB_RETRY_ATTEMPTS
from src.utils.logger import get_logger

# Setup logger
logger = get_logger(__name__)


class DatabaseService:
    """
    Service class untuk operasi database dengan connection pooling dan error handling.
    """
    
    def __init__(self):
        """Initialize database service."""
        self.db_params = self._parse_database_url(DATABASE_URL)
        if not self.db_params:
            raise ValueError("Invalid DATABASE_URL format")
    
    def _parse_database_url(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Parse DATABASE_URL menjadi komponen-komponen koneksi.
        
        Args:
            url: DATABASE_URL string
            
        Returns:
            Dict dengan komponen koneksi atau None jika gagal
        """
        try:
            # Hapus prefix 'postgresql://'
            url = url.replace('postgresql://', '')
            
            # Split user:password@host:port/database
            auth, rest = url.split('@')
            user, password = auth.split(':')
            
            host_port, database = rest.split('/')
            
            if ':' in host_port:
                host, port = host_port.split(':')
                port = int(port)
            else:
                host = host_port
                port = 5432
            
            return {
                'user': user,
                'password': password,
                'host': host,
                'port': port,
                'database': database
            }
        except Exception as e:
            logger.error(f"Failed to parse DATABASE_URL: {e}")
            return None
    
    @contextmanager
    def get_connection(self):
        """
        Context manager untuk koneksi database dengan auto-cleanup.
        
        Yields:
            psycopg2.connection: Database connection
        """
        connection = None
        try:
            connection = self._create_connection()
            yield connection
        except Exception as e:
            if connection:
                connection.rollback()
            raise e
        finally:
            if connection:
                connection.close()
    
    def _create_connection(self):
        """
        Membuat koneksi ke database dengan retry logic.
        
        Returns:
            psycopg2.connection: Database connection
            
        Raises:
            OperationalError: Jika semua percobaan koneksi gagal
        """
        last_error = None
        
        for attempt in range(DB_RETRY_ATTEMPTS):
            try:
                logger.info(f"Database connection attempt {attempt + 1}/{DB_RETRY_ATTEMPTS}...")
                
                connection = psycopg2.connect(
                    user=self.db_params['user'],
                    password=self.db_params['password'],
                    host=self.db_params['host'],
                    port=self.db_params['port'],
                    database=self.db_params['database'],
                    connect_timeout=DB_CONNECTION_TIMEOUT,
                    options="-c statement_timeout=30000"
                )
                
                logger.info("Database connection successful!")
                return connection
                
            except (OperationalError, socket.timeout) as e:
                last_error = e
                logger.warning(f"Connection attempt {attempt + 1} failed: {str(e)[:100]}")
                
                if attempt < DB_RETRY_ATTEMPTS - 1:
                    logger.info("Retrying in 2 seconds...")
                    time.sleep(2)
                continue
        
        # Jika semua percobaan gagal
        error_msg = f"Failed to connect after {DB_RETRY_ATTEMPTS} attempts: {str(last_error)}"
        logger.error(error_msg)
        raise OperationalError(error_msg)
    
    def get_component_rpn(self, component_name: str) -> Tuple[Optional[float], Optional[float]]:
        """
        Mengambil nilai RPN untuk komponen tertentu.
        
        Args:
            component_name: Nama komponen
            
        Returns:
            Tuple (rpn_value, rpn_max) atau (None, None) jika tidak ditemukan
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Query RPN value untuk komponen tertentu
                    query_rpn = sql.SQL(
                        "SELECT rpn_value FROM components WHERE name = %s"
                    )
                    cursor.execute(query_rpn, (component_name,))
                    result = cursor.fetchone()
                    
                    if result is None:
                        logger.warning(f"Component '{component_name}' not found in database")
                        return None, None
                    
                    rpn_value = result[0]
                    
                    # Query nilai MAX(rpn_value)
                    cursor.execute("SELECT MAX(rpn_value) FROM components")
                    max_result = cursor.fetchone()
                    rpn_max = max_result[0] if max_result[0] else 210
                    
                    logger.info(f"Component '{component_name}': RPN={rpn_value}, MAX={rpn_max}")
                    return rpn_value, rpn_max
                    
        except OperationalError as e:
            logger.error(f"Database connection error: {e}")
            return None, None
        except Exception as e:
            logger.error(f"Database query error: {e}")
            return None, None
    
    def get_all_components(self) -> Optional[List[Tuple]]:
        """
        Mengambil daftar semua komponen.
        
        Returns:
            List of tuples (id, name, rpn_value) atau None jika error
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = "SELECT id, name, rpn_value FROM components ORDER BY name"
                    cursor.execute(query)
                    results = cursor.fetchall()
                    
                    logger.info(f"Retrieved {len(results)} components from database")
                    return results
                    
        except OperationalError as e:
            logger.error(f"Database connection failed: {e}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving components: {e}")
            return None
    
    def test_connection(self) -> bool:
        """
        Test koneksi database.
        
        Returns:
            bool: True jika koneksi berhasil, False jika gagal
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("SELECT 1")
                    
            logger.info("Database connection test passed!")
            return True
        except Exception as e:
            logger.error(f"Database connection test failed: {e}")
            return False

    def log_machine_status(self, data):
        """
        Menyimpan log status mesin dari MQTT ke database.
        Includes cumulative production and defects data.
        """
        insert_sql = (
            """
            INSERT INTO machine_logs (
                timestamp, 
                machine_status, 
                performance_rate, 
                quality_rate,
                cumulative_production,
                cumulative_defects
            )
            VALUES (%s, %s, %s, %s, %s, %s);
            """
        )
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(
                        insert_sql,
                        (
                            data.get('timestamp'),
                            data.get('machine_status'),
                            data.get('performance_rate'),
                            data.get('quality_rate'),
                            data.get('cumulative_production', 0),  # Default 0 if not present
                            data.get('cumulative_defects', 0),     # Default 0 if not present
                        ),
                    )
                conn.commit()
            logger.info(f"Machine status logged: Production={data.get('cumulative_production', 0)}, Defects={data.get('cumulative_defects', 0)}")
        except Exception as e:
            logger.error(f"Database error while logging machine status: {e}")

    def get_latest_machine_status(self) -> Optional[Dict[str, Any]]:
        """
        Mengambil status mesin terbaru dari database.
        Includes cumulative production and defects data.
        
        Returns:
            Dict dengan keys: timestamp, machine_status, performance_rate, quality_rate,
            cumulative_production, cumulative_defects
            atau None jika tidak ada data
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT 
                            timestamp, 
                            machine_status, 
                            performance_rate, 
                            quality_rate,
                            cumulative_production,
                            cumulative_defects
                        FROM machine_logs
                        ORDER BY timestamp DESC
                        LIMIT 1
                    """
                    cursor.execute(query)
                    result = cursor.fetchone()
                    
                    if result is None:
                        logger.warning("No machine status data found in database")
                        return None
                    
                    data = {
                        "timestamp": result[0],
                        "machine_status": result[1],
                        "performance_rate": result[2],
                        "quality_rate": result[3],
                        "cumulative_production": result[4] if result[4] is not None else 0,
                        "cumulative_defects": result[5] if result[5] is not None else 0
                    }
                    
                    logger.info(f"Latest machine status: Status={data['machine_status']}, Production={data['cumulative_production']}, Defects={data['cumulative_defects']}")
                    return data
                    
        except OperationalError as e:
            logger.error(f"Database connection error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving latest machine status: {e}")
            return None

    def get_recent_machine_logs(self, limit: int = 100) -> Optional[List[Dict[str, Any]]]:
        """
        Mengambil sejumlah log mesin terbaru dari database.
        Digunakan untuk menghitung Availability berdasarkan histori status.
        
        Args:
            limit: Jumlah log yang diambil (default 100)
            
        Returns:
            List of Dict dengan keys: timestamp, machine_status, performance_rate, quality_rate
            atau None jika tidak ada data
        """
        try:
            with self.get_connection() as conn:
                with conn.cursor() as cursor:
                    query = """
                        SELECT timestamp, machine_status, performance_rate, quality_rate
                        FROM machine_logs
                        ORDER BY timestamp DESC
                        LIMIT %s
                    """
                    cursor.execute(query, (limit,))
                    results = cursor.fetchall()
                    
                    if not results:
                        logger.warning("No machine logs found in database")
                        return None
                    
                    # Convert to list of dicts
                    logs = []
                    for row in results:
                        logs.append({
                            "timestamp": row[0],
                            "machine_status": row[1],
                            "performance_rate": row[2],
                            "quality_rate": row[3]
                        })
                    
                    logger.info(f"Retrieved {len(logs)} machine logs from database")
                    return logs
                    
        except OperationalError as e:
            logger.error(f"Database connection error: {e}")
            return None
        except Exception as e:
            logger.error(f"Error retrieving machine logs: {e}")
            return None


# Global database service instance
db_service = DatabaseService()


# Backward compatibility functions
def get_rpn_value_from_db(component_name: str) -> Tuple[Optional[float], Optional[float]]:
    """Compatibility wrapper untuk get_component_rpn."""
    return db_service.get_component_rpn(component_name)


def get_all_components_from_db() -> Optional[List[Tuple]]:
    """Compatibility wrapper untuk get_all_components."""
    return db_service.get_all_components()


def test_database_connection() -> bool:
    """Compatibility wrapper untuk test_connection."""
    return db_service.test_connection()

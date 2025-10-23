"""
Database Migration Script
Run this to add cumulative_production and cumulative_defects columns to machine_logs table
"""

import psycopg2
from config import DATABASE_URL
from src.utils.logger import get_logger

logger = get_logger(__name__)

def parse_database_url(url: str):
    """Parse DATABASE_URL into connection parameters."""
    try:
        url = url.replace('postgresql://', '')
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

def run_migration():
    """Run the database migration."""
    logger.info("🔄 Starting database migration...")
    
    # Parse database URL
    db_params = parse_database_url(DATABASE_URL)
    if not db_params:
        logger.error("❌ Invalid DATABASE_URL")
        return False
    
    try:
        # Connect to database
        logger.info(f" Connecting to database: {db_params['host']}:{db_params['port']}/{db_params['database']}")
        conn = psycopg2.connect(
            user=db_params['user'],
            password=db_params['password'],
            host=db_params['host'],
            port=db_params['port'],
            database=db_params['database']
        )
        
        cursor = conn.cursor()
        
        # Read migration SQL
        logger.info("📄 Reading migration script...")
        with open('migrations/add_cumulative_columns.sql', 'r') as f:
            migration_sql = f.read()
        
        # Execute migration
        logger.info("⚡ Executing migration...")
        cursor.execute(migration_sql)
        conn.commit()
        
        # Verify migration
        logger.info("✅ Verifying migration...")
        cursor.execute("""
            SELECT column_name, data_type, column_default, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'machine_logs'
            ORDER BY ordinal_position;
        """)
        
        columns = cursor.fetchall()
        logger.info("📊 Current machine_logs schema:")
        for col in columns:
            logger.info(f"  - {col[0]}: {col[1]} (default: {col[2]}, nullable: {col[3]})")
        
        # Check if new columns exist
        column_names = [col[0] for col in columns]
        if 'cumulative_production' in column_names and 'cumulative_defects' in column_names:
            logger.info("✅ Migration successful! New columns added:")
            logger.info("  - cumulative_production (INTEGER)")
            logger.info("  - cumulative_defects (INTEGER)")
            success = True
        else:
            logger.error("❌ Migration failed: Columns not found after migration")
            success = False
        
        cursor.close()
        conn.close()
        
        return success
        
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        if conn:
            conn.rollback()
        return False

if __name__ == "__main__":
    print("\n" + "="*70)
    print("DATABASE MIGRATION: Add Cumulative Columns")
    print("="*70 + "\n")
    
    success = run_migration()
    
    if success:
        print("\n" + "="*70)
        print("✅ MIGRATION COMPLETED SUCCESSFULLY")
        print("="*70)
        print("\nYou can now:")
        print("1. Run sensor_simulator.py to send cumulative data")
        print("2. Backend will automatically log cumulative values")
        print("3. Auto-prediction will use real production data")
        print("="*70 + "\n")
    else:
        print("\n" + "="*70)
        print("❌ MIGRATION FAILED")
        print("="*70)
        print("\nPlease check the error messages above.")
        print("="*70 + "\n")

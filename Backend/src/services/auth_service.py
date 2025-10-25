"""
Authentication Service

Service untuk menangani authentication dan authorization user:
- User registration
- User login/logout  
- Password hashing
- Session management
- Role-based access control
"""

import bcrypt
import secrets
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, List
from .database_service import DatabaseService

logger = logging.getLogger(__name__)

class AuthService:
    def __init__(self):
        self.db_service = DatabaseService()
        
    def hash_password(self, password: str) -> str:
        """Hash password menggunakan bcrypt"""
        salt = bcrypt.gensalt()
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    def verify_password(self, password: str, hashed: str) -> bool:
        """Verifikasi password dengan hash"""
        try:
            return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
        except Exception as e:
            logger.error(f"Password verification error: {e}")
            return False
    
    def register_user(self, username: str, email: str, password: str, 
                     full_name: str = None, role: str = 'user') -> Tuple[bool, str]:
        """
        Register user baru
        
        Returns:
        - (True, "success message") jika berhasil
        - (False, "error message") jika gagal
        """
        try:
            # Validasi input
            if len(username) < 3:
                return False, "Username minimal 3 karakter"
            
            if len(password) < 6:
                return False, "Password minimal 6 karakter"
            
            if role not in ['admin', 'user', 'operator']:
                return False, "Role tidak valid"
            
            # Hash password
            password_hash = self.hash_password(password)
            
            with self.db_service.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Check apakah username/email sudah ada
                    cursor.execute(
                        "SELECT id FROM users WHERE username = %s OR email = %s",
                        (username, email)
                    )
                    
                    if cursor.fetchone():
                        return False, "Username atau email sudah digunakan"
                    
                    # Insert user baru
                    cursor.execute("""
                        INSERT INTO users (username, email, password_hash, full_name, role)
                        VALUES (%s, %s, %s, %s, %s)
                        RETURNING id
                    """, (username, email, password_hash, full_name, role))
                    
                    user_id = cursor.fetchone()[0]
                    conn.commit()
                    
                    logger.info(f"User registered successfully: {username} (ID: {user_id})")
                    return True, "User berhasil didaftarkan"
                    
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False, f"Gagal mendaftarkan user: {str(e)}"
    
    def authenticate_user(self, username: str, password: str, ip_address: str = None,
                         user_agent: str = None) -> Tuple[bool, str, Optional[Dict]]:
        """
        Authenticate user login
        
        Returns:
        - (True, session_token, user_data) jika berhasil
        - (False, error_message, None) jika gagal
        """
        try:
            with self.db_service.get_connection() as conn:
                with conn.cursor() as cursor:
                    # Get user data
                    cursor.execute("""
                        SELECT id, username, email, password_hash, full_name, role, 
                               is_active, login_attempts, locked_until
                        FROM users 
                        WHERE username = %s OR email = %s
                    """, (username, username))
                    
                    user_row = cursor.fetchone()
                    
                    if not user_row:
                        return False, "Username atau password salah", None
                    
                    user_id, db_username, email, password_hash, full_name, role, \
                    is_active, login_attempts, locked_until = user_row
                    
                    # Check apakah user aktif
                    if not is_active:
                        return False, "Akun tidak aktif", None
                    
                    # Check apakah akun terkunci
                    if locked_until and locked_until > datetime.now():
                        return False, f"Akun terkunci sampai {locked_until.strftime('%Y-%m-%d %H:%M:%S')}", None
                    
                    # Verify password
                    if not self.verify_password(password, password_hash):
                        # Increment login attempts
                        new_attempts = login_attempts + 1
                        locked_until_new = None
                        
                        # Lock account after 5 failed attempts
                        if new_attempts >= 5:
                            locked_until_new = datetime.now() + timedelta(minutes=15)
                        
                        cursor.execute("""
                            UPDATE users 
                            SET login_attempts = %s, locked_until = %s
                            WHERE id = %s
                        """, (new_attempts, locked_until_new, user_id))
                        
                        conn.commit()
                        
                        if locked_until_new:
                            return False, "Akun terkunci karena terlalu banyak percobaan login gagal", None
                        else:
                            return False, f"Username atau password salah (percobaan {new_attempts}/5)", None
                    
                    # Reset login attempts jika berhasil
                    cursor.execute("""
                        UPDATE users 
                        SET login_attempts = 0, locked_until = NULL, last_login = CURRENT_TIMESTAMP
                        WHERE id = %s
                    """, (user_id,))
                    
                    # Generate session token
                    session_token = secrets.token_urlsafe(32)
                    expires_at = datetime.now() + timedelta(hours=24)  # Session 24 jam
                    
                    # Save session
                    cursor.execute("""
                        INSERT INTO user_sessions (user_id, session_token, expires_at, ip_address, user_agent)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (user_id, session_token, expires_at, ip_address, user_agent))
                    
                    conn.commit()
                    
                    user_data = {
                        'id': user_id,
                        'username': db_username,
                        'email': email,
                        'full_name': full_name,
                        'role': role,
                        'session_token': session_token,
                        'expires_at': expires_at.isoformat()
                    }
                    
                    logger.info(f"User authenticated successfully: {db_username}")
                    return True, session_token, user_data
                    
        except Exception as e:
            logger.error(f"Authentication error: {e}")
            return False, f"Gagal login: {str(e)}", None
    
    def validate_session(self, session_token: str) -> Optional[Dict]:
        """
        Validasi session token dan return user data
        
        Returns:
        - User data dict jika session valid
        - None jika session tidak valid/expired
        """
        try:
            with self.db_service.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT u.id, u.username, u.email, u.full_name, u.role, u.is_active,
                               s.expires_at
                        FROM users u
                        JOIN user_sessions s ON u.id = s.user_id
                        WHERE s.session_token = %s AND s.expires_at > CURRENT_TIMESTAMP
                    """, (session_token,))
                    
                    row = cursor.fetchone()
                    
                    if not row:
                        return None
                    
                    user_id, username, email, full_name, role, is_active, expires_at = row
                    
                    if not is_active:
                        return None
                    
                    return {
                        'id': user_id,
                        'username': username,
                        'email': email,
                        'full_name': full_name,
                        'role': role,
                        'expires_at': expires_at.isoformat()
                    }
                    
        except Exception as e:
            logger.error(f"Session validation error: {e}")
            return None
    
    def logout_user(self, session_token: str) -> bool:
        """Logout user dengan menghapus session"""
        try:
            with self.db_service.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM user_sessions WHERE session_token = %s",
                        (session_token,)
                    )
                    
                    conn.commit()
                    deleted_count = cursor.rowcount
                    
                    if deleted_count > 0:
                        logger.info("User logged out successfully")
                        return True
                    else:
                        logger.warning("Session not found for logout")
                        return False
                        
        except Exception as e:
            logger.error(f"Logout error: {e}")
            return False
    
    def cleanup_expired_sessions(self) -> int:
        """Bersihkan session yang sudah expired"""
        try:
            with self.db_service.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP"
                    )
                    
                    conn.commit()
                    deleted_count = cursor.rowcount
                    
                    if deleted_count > 0:
                        logger.info(f"Cleaned up {deleted_count} expired sessions")
                    
                    return deleted_count
                    
        except Exception as e:
            logger.error(f"Session cleanup error: {e}")
            return 0
    
    def get_all_users(self) -> List[Dict]:
        """Get semua user untuk admin dashboard"""
        try:
            with self.db_service.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, username, email, full_name, role, is_active, 
                               created_at, last_login, login_attempts
                        FROM users
                        ORDER BY created_at DESC
                    """)
                    
                    users = []
                    for row in cursor.fetchall():
                        user_id, username, email, full_name, role, is_active, \
                        created_at, last_login, login_attempts = row
                        
                        users.append({
                            'id': user_id,
                            'username': username,
                            'email': email,
                            'full_name': full_name,
                            'role': role,
                            'is_active': is_active,
                            'created_at': created_at.isoformat() if created_at else None,
                            'last_login': last_login.isoformat() if last_login else None,
                            'login_attempts': login_attempts
                        })
                    
                    return users
                    
        except Exception as e:
            logger.error(f"Get users error: {e}")
            return []

# Create global instance
auth_service = AuthService()
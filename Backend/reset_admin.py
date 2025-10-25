#!/usr/bin/env python3
"""
Reset admin password
"""

from src.services.auth_service import auth_service
from src.services.database_service import db_service

def reset_admin_password():
    print('=== RESETTING ADMIN PASSWORD ===')
    
    # Generate new hash using auth_service method
    new_hash = auth_service.hash_password('admin123')
    print(f'Generated new hash: {new_hash[:20]}...')
    
    # Update in database
    with db_service.get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute('UPDATE users SET password_hash = %s, login_attempts = 0, locked_until = NULL WHERE username = %s', (new_hash, 'admin'))
            conn.commit()
            print('✅ Admin password reset successfully')
    
    # Test login
    print('\nTesting admin login...')
    success, token, user_data = auth_service.authenticate_user('admin', 'admin123')
    
    if success:
        print('✅ Admin login successful!')
        print(f'Username: {user_data["username"]}')
        print(f'Role: {user_data["role"]}')
        print(f'Token: {token[:20]}...')
        
        # Test session validation
        print('\nTesting session validation...')
        validated = auth_service.validate_session(token)
        if validated:
            print('✅ Session validation successful')
        else:
            print('❌ Session validation failed')
            
    else:
        print(f'❌ Login failed: {token}')

if __name__ == '__main__':
    reset_admin_password()
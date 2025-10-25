#!/usr/bin/env python3
"""
Generate correct password hashes for default users
"""

import bcrypt

def generate_password_hash(password):
    """Generate bcrypt hash for password"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password, hashed):
    """Verify password with hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

if __name__ == '__main__':
    print('=== PASSWORD HASH GENERATOR ===')
    
    # Generate hashes for default users
    admin_password = 'admin123'
    operator_password = 'operator123'
    
    admin_hash = generate_password_hash(admin_password)
    operator_hash = generate_password_hash(operator_password)
    
    print(f'Admin password: {admin_password}')
    print(f'Admin hash: {admin_hash}')
    print(f'Admin verification: {verify_password(admin_password, admin_hash)}')
    print()
    
    print(f'Operator password: {operator_password}')
    print(f'Operator hash: {operator_hash}')
    print(f'Operator verification: {verify_password(operator_password, operator_hash)}')
    print()
    
    print('UPDATE SQL:')
    print(f"UPDATE users SET password_hash = '{admin_hash}' WHERE username = 'admin';")
    print(f"UPDATE users SET password_hash = '{operator_hash}' WHERE username = 'operator';")
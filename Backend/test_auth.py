#!/usr/bin/env python3
"""
Test script untuk authentication system
"""

from src.services.auth_service import auth_service

def test_auth_system():
    print('=== TESTING AUTH SERVICE ===')

    # Test 1: Login dengan admin
    print('1. Testing admin login...')
    success, token, user_data = auth_service.authenticate_user('admin', 'admin123')

    if success:
        print('✅ Admin login successful')
        print(f'  Username: {user_data["username"]}')
        print(f'  Role: {user_data["role"]}')
        print(f'  Token: {token[:20]}...')
        
        # Test 2: Validate session
        print('\n2. Testing session validation...')
        validated_user = auth_service.validate_session(token)
        
        if validated_user:
            print('✅ Session validation successful')
            print(f'  User: {validated_user["username"]} ({validated_user["role"]})')
        else:
            print('❌ Session validation failed')
            
        # Test 3: Get all users
        print('\n3. Testing get all users...')
        users = auth_service.get_all_users()
        print(f'Total users: {len(users)}')
        for user in users:
            status = 'Active' if user['is_active'] else 'Inactive'
            print(f'  - {user["username"]} ({user["role"]}) - {status}')
            
        # Test 4: Logout
        print('\n4. Testing logout...')
        logout_success = auth_service.logout_user(token)
        
        if logout_success:
            print('✅ Logout successful')
            
            # Verify session invalidated
            validated_user = auth_service.validate_session(token)
            if not validated_user:
                print('✅ Session invalidated after logout')
            else:
                print('❌ Session still valid after logout')
        else:
            print('❌ Logout failed')
            
    else:
        print(f'❌ Admin login failed: {token}')

    # Test 5: Register new user
    print('\n5. Testing user registration...')
    success, message = auth_service.register_user(
        username='testuser2',
        email='testuser2@flexo104.com', 
        password='test123',
        full_name='Test User 2',
        role='user'
    )
    
    if success:
        print('✅ User registration successful')
        
        # Test login with new user
        print('\n6. Testing login with new user...')
        success, token, user_data = auth_service.authenticate_user('testuser2', 'test123')
        
        if success:
            print('✅ New user login successful')
            print(f'  Username: {user_data["username"]}')
            print(f'  Role: {user_data["role"]}')
        else:
            print(f'❌ New user login failed: {token}')
    else:
        print(f'❌ Registration failed: {message}')

    print('\n=== AUTH SERVICE TEST COMPLETED ===')

if __name__ == '__main__':
    test_auth_system()
"""
Authentication Controller

Controller untuk menangani endpoint authentication:
- POST /api/auth/register - User registration
- POST /api/auth/login - User login
- POST /api/auth/logout - User logout
- GET /api/auth/me - Get current user info
- GET /api/auth/users - Get all users (admin only)
"""

import logging
from flask import Blueprint, request, jsonify, session
from ..services.auth_service import auth_service
from functools import wraps

logger = logging.getLogger(__name__)

# Create blueprint
auth_bp = Blueprint('auth', __name__)

def require_auth(f):
    """Decorator untuk memerlukan authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        auth_header = request.headers.get('Authorization')
        
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({
                'success': False,
                'error': 'Authentication required',
                'message': 'Token tidak ditemukan'
            }), 401
        
        token = auth_header.split(' ')[1]
        user_data = auth_service.validate_session(token)
        
        if not user_data:
            return jsonify({
                'success': False,
                'error': 'Invalid token',
                'message': 'Token tidak valid atau sudah expired'
            }), 401
        
        # Set user data untuk digunakan di route
        request.current_user = user_data
        return f(*args, **kwargs)
    
    return decorated_function

def require_admin(f):
    """Decorator untuk memerlukan role admin"""
    @wraps(f)
    @require_auth
    def decorated_function(*args, **kwargs):
        if request.current_user.get('role') != 'admin':
            return jsonify({
                'success': False,
                'error': 'Access denied',
                'message': 'Hanya admin yang dapat mengakses'
            }), 403
        
        return f(*args, **kwargs)
    
    return decorated_function

@auth_bp.route('/auth/register', methods=['POST'])
def register():
    """
    POST /api/auth/register
    
    Register user baru.
    
    JSON Body:
    {
        "username": "string",
        "email": "string", 
        "password": "string",
        "full_name": "string (optional)",
        "role": "string (optional, default: user)"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Invalid request',
                'message': 'Data JSON diperlukan'
            }), 400
        
        # Validasi required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'error': 'Missing field',
                    'message': f'Field {field} diperlukan'
                }), 400
        
        username = data['username'].strip()
        email = data['email'].strip()
        password = data['password']
        full_name = data.get('full_name', '').strip()
        role = data.get('role', 'user').strip()
        
        # Register user
        success, message = auth_service.register_user(
            username=username,
            email=email, 
            password=password,
            full_name=full_name or None,
            role=role
        )
        
        if success:
            logger.info(f"New user registered: {username}")
            return jsonify({
                'success': True,
                'message': message
            }), 201
        else:
            return jsonify({
                'success': False,
                'error': 'Registration failed',
                'message': message
            }), 400
            
    except Exception as e:
        logger.error(f"Registration error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@auth_bp.route('/auth/login', methods=['POST'])
def login():
    """
    POST /api/auth/login
    
    User login.
    
    JSON Body:
    {
        "username": "string",  // bisa username atau email
        "password": "string"
    }
    """
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({
                'success': False,
                'error': 'Invalid request', 
                'message': 'Data JSON diperlukan'
            }), 400
        
        username = data.get('username', '').strip()
        password = data.get('password', '')
        
        if not username or not password:
            return jsonify({
                'success': False,
                'error': 'Missing credentials',
                'message': 'Username dan password diperlukan'
            }), 400
        
        # Get client info
        ip_address = request.remote_addr
        user_agent = request.headers.get('User-Agent')
        
        # Authenticate
        success, result, user_data = auth_service.authenticate_user(
            username=username,
            password=password,
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        if success:
            logger.info(f"User login successful: {user_data['username']}")
            return jsonify({
                'success': True,
                'message': 'Login berhasil',
                'data': {
                    'user': {
                        'id': user_data['id'],
                        'username': user_data['username'],
                        'email': user_data['email'],
                        'full_name': user_data['full_name'],
                        'role': user_data['role']
                    },
                    'token': user_data['session_token'],
                    'expires_at': user_data['expires_at']
                }
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Authentication failed',
                'message': result
            }), 401
            
    except Exception as e:
        logger.error(f"Login error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@auth_bp.route('/auth/logout', methods=['POST'])
@require_auth
def logout():
    """
    POST /api/auth/logout
    
    User logout.
    
    Headers:
    Authorization: Bearer <token>
    """
    try:
        auth_header = request.headers.get('Authorization')
        token = auth_header.split(' ')[1]
        
        success = auth_service.logout_user(token)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Logout berhasil'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Logout failed',
                'message': 'Gagal logout'
            }), 400
            
    except Exception as e:
        logger.error(f"Logout error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@auth_bp.route('/auth/me', methods=['GET'])
@require_auth
def get_current_user():
    """
    GET /api/auth/me
    
    Get informasi user yang sedang login.
    
    Headers:
    Authorization: Bearer <token>
    """
    try:
        user_data = request.current_user
        
        return jsonify({
            'success': True,
            'data': {
                'id': user_data['id'],
                'username': user_data['username'],
                'email': user_data['email'],
                'full_name': user_data['full_name'],
                'role': user_data['role'],
                'expires_at': user_data['expires_at']
            }
        }), 200
        
    except Exception as e:
        logger.error(f"Get current user error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@auth_bp.route('/auth/users', methods=['GET'])
@require_admin
def get_all_users():
    """
    GET /api/auth/users
    
    Get semua user (hanya untuk admin).
    
    Headers:
    Authorization: Bearer <token>
    """
    try:
        users = auth_service.get_all_users()
        
        return jsonify({
            'success': True,
            'count': len(users),
            'data': users
        }), 200
        
    except Exception as e:
        logger.error(f"Get all users error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@auth_bp.route('/auth/cleanup-sessions', methods=['POST'])
@require_admin
def cleanup_expired_sessions():
    """
    POST /api/auth/cleanup-sessions
    
    Bersihkan session yang expired (admin only).
    
    Headers:
    Authorization: Bearer <token>
    """
    try:
        deleted_count = auth_service.cleanup_expired_sessions()
        
        return jsonify({
            'success': True,
            'message': f'Berhasil membersihkan {deleted_count} session expired'
        }), 200
        
    except Exception as e:
        logger.error(f"Session cleanup error: {e}")
        return jsonify({
            'success': False,
            'error': 'Internal server error',
            'message': str(e)
        }), 500
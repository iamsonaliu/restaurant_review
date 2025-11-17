import bcrypt
import jwt
import datetime
from flask import current_app
from functools import wraps
from flask import request, jsonify

def hash_password(password):
    """Hash a password"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password, hashed):
    """Verify a password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

def create_token(user_id):
    """Create JWT token"""
    payload = {
        'user_id': user_id,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, current_app.config['JWT_SECRET_KEY'], algorithm='HS256')

def decode_token(token):
    """Decode JWT token"""
    try:
        return jwt.decode(token, current_app.config['JWT_SECRET_KEY'], algorithms=['HS256'])
    except:
        return None

def token_required(f):
    """Decorator for protected routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None

        # Accept both "Authorization" and "authorization"
        auth_header = request.headers.get('Authorization') or request.headers.get('authorization')

        # Parse Bearer token
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        # Fallback for older clients
        if not token:
            token = request.headers.get('x-access-token')

        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        # Decode token
        payload = decode_token(token)
        if not payload:
            return jsonify({'error': 'Invalid token'}), 401

        # Attach user_id to request
        request.user_id = payload['user_id']
        return f(*args, **kwargs)

    return decorated

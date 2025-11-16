from flask import Blueprint, request, jsonify
from app.database import db
from app.utils.auth_helpers import hash_password, verify_password, create_token
import uuid
import traceback

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST', 'OPTIONS'])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate input
        if not data.get('email') or not data.get('password') or not data.get('username'):
            return jsonify({'error': 'Email, username, and password are required'}), 400
        
        # Check if user exists
        existing = db.execute_query(
            "SELECT user_id FROM USERS WHERE email = :email",
            {'email': data['email']},
            fetch_one=True
        )
        
        if existing:
            return jsonify({'error': 'Email already registered'}), 400
        
        # Create user
        user_id = f"U{uuid.uuid4().hex[:8].upper()}"
        hashed_pw = hash_password(data['password'])
        
        result = db.execute_non_query(
            """INSERT INTO USERS (user_id, username, email, password_hash, registration_date)
               VALUES (:user_id, :username, :email, :password_hash, SYSDATE)""",
            {
                'user_id': user_id,
                'username': data['username'],
                'email': data['email'],
                'password_hash': hashed_pw
            }
        )
        
        success = result is not None and result.get('rowcount', 0) > 0
        
        if success:
            token = create_token(user_id)
            return jsonify({
                'message': 'User registered successfully',
                'token': token,
                'user': {
                    'user_id': user_id,
                    'username': data['username'],
                    'email': data['email']
                }
            }), 201
        else:
            return jsonify({'error': 'Registration failed'}), 500
            
    except Exception as e:
        print(f"Registration error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Registration failed', 'message': str(e)}), 500

@bp.route('/login', methods=['POST', 'OPTIONS'])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    
    try:
        data = request.get_json()
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Email and password are required'}), 400
        
        # Get user
        user = db.execute_query(
            """SELECT user_id, username, email, password_hash, role
               FROM USERS WHERE email = :email""",
            {'email': data['email']},
            fetch_one=True
        )
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not verify_password(data['password'], user['password_hash']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Create token
        token = create_token(user['user_id'])
        
        return jsonify({
            'message': 'Login successful',
            'token': token,
            'user': {
                'user_id': user['user_id'],
                'username': user['username'],
                'email': user['email'],
                'role': user.get('role', 'user')
            }
        }), 200
        
    except Exception as e:
        print(f"Login error: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Login failed', 'message': str(e)}), 500
from flask import Blueprint, request, jsonify
from app.database import db
from app.utils.auth_helpers import hash_password, verify_password, create_token
import uuid

bp = Blueprint('auth', __name__)

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # Validate input
    if not data.get('email') or not data.get('password') or not data.get('username'):
        return jsonify({'error': 'Email, username, and password are required'}), 400
    
    # Check if user exists
    existing = db.execute_query(
        "SELECT user_id FROM USERS WHERE email = :1",
        (data['email'],),
        fetch_one=True
    )
    
    if existing:
        return jsonify({'error': 'Email already registered'}), 400
    
    # Create user
    user_id = f"U{uuid.uuid4().hex[:8].upper()}"
    hashed_pw = hash_password(data['password'])
    
    success = db.execute_update(
        """INSERT INTO USERS (user_id, username, email, password_hash)
           VALUES (:1, :2, :3, :4)""",
        (user_id, data['username'], data['email'], hashed_pw)
    )
    
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

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    if not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password are required'}), 400
    
    # Get user
    user = db.execute_query(
        """SELECT user_id, username, email, password_hash, role
           FROM USERS WHERE email = :1""",
        (data['email'],),
        fetch_one=True
    )
    
    if not user:
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Verify password
    if not verify_password(data['password'], user[3]):
        return jsonify({'error': 'Invalid credentials'}), 401
    
    # Create token
    token = create_token(user[0])
    
    return jsonify({
        'message': 'Login successful',
        'token': token,
        'user': {
            'user_id': user[0],
            'username': user[1],
            'email': user[2],
            'role': user[4]
        }
    }), 200
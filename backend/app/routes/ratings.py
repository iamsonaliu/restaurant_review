from flask import Blueprint, request, jsonify
from app.database import db
from app.utils.auth_helpers import token_required
import uuid

bp = Blueprint('ratings', __name__)

@bp.route('/', methods=['POST'])
@token_required
def create_rating():
    """Create or update rating"""
    data = request.get_json()
    
    if not data.get('restaurant_id') or not data.get('rating_value'):
        return jsonify({'error': 'Restaurant ID and rating value are required'}), 400
    
    if not (1 <= float(data['rating_value']) <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    # Check if user already rated
    existing = db.execute_query(
        "SELECT rating_id FROM RATINGS WHERE user_id = :1 AND restaurant_id = :2",
        (request.user_id, data['restaurant_id']),
        fetch_one=True
    )
    
    if existing:
        # Update existing rating
        success = db.execute_update(
            "UPDATE RATINGS SET rating_value = :1 WHERE rating_id = :2",
            (data['rating_value'], existing[0])
        )
        message = 'Rating updated successfully'
    else:
        # Create new rating
        rating_id = f"RAT{uuid.uuid4().hex[:8].upper()}"
        success = db.execute_update(
            """INSERT INTO RATINGS (rating_id, user_id, restaurant_id, rating_value)
               VALUES (:1, :2, :3, :4)""",
            (rating_id, request.user_id, data['restaurant_id'], data['rating_value'])
        )
        message = 'Rating created successfully'
    
    if success:
        return jsonify({'message': message}), 201
    else:
        return jsonify({'error': 'Failed to submit rating'}), 500

@bp.route('/user', methods=['GET'])
@token_required
def get_user_ratings():
    """Get all ratings by current user"""
    query = """
        SELECT rat.rating_id, rat.restaurant_id, r.name, rat.rating_value, rat.rating_date
        FROM RATINGS rat
        JOIN RESTAURANTS r ON rat.restaurant_id = r.restaurant_id
        WHERE rat.user_id = :1
        ORDER BY rat.rating_date DESC
    """
    
    ratings = db.execute_query(query, (request.user_id,))
    
    result = []
    for r in ratings:
        result.append({
            'rating_id': r[0],
            'restaurant_id': r[1],
            'restaurant_name': r[2],
            'rating_value': float(r[3]),
            'rating_date': r[4].strftime('%Y-%m-%d') if r[4] else None
        })
    
    return jsonify(result), 200
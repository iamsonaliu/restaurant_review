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
    
    rating_value = float(data['rating_value'])
    if not (1 <= rating_value <= 5):
        return jsonify({'error': 'Rating must be between 1 and 5'}), 400
    
    try:
        # Check if user already rated
        existing = db.execute_query(
            "SELECT rating_id FROM RATINGS WHERE user_id = :user_id AND restaurant_id = :restaurant_id",
            {'user_id': request.user_id, 'restaurant_id': data['restaurant_id']},
            fetch_one=True
        )
        
        if existing:
            # Update existing rating
            result = db.execute_non_query(
                "UPDATE RATINGS SET rating_value = :rating_value WHERE rating_id = :rating_id",
                {'rating_value': rating_value, 'rating_id': existing['rating_id']}
            )
            success = result is not None and result.get('rowcount', 0) > 0
            message = 'Rating updated successfully'
        else:
            # Create new rating
            rating_id = f"RAT{uuid.uuid4().hex[:8].upper()}"
            result = db.execute_non_query(
                """INSERT INTO RATINGS (rating_id, user_id, restaurant_id, rating_value)
                   VALUES (:rating_id, :user_id, :restaurant_id, :rating_value)""",
                {
                    'rating_id': rating_id,
                    'user_id': request.user_id,
                    'restaurant_id': data['restaurant_id'],
                    'rating_value': rating_value
                }
            )
            success = result is not None and result.get('rowcount', 0) > 0
            message = 'Rating created successfully'
        
        if success:
            return jsonify({'message': message}), 201
        else:
            print(f"ERROR: Rating insert/update failed. Result: {result}")
            return jsonify({'error': 'Failed to submit rating', 'message': 'Database operation returned no rows affected'}), 500
    except Exception as e:
        print(f"ERROR in create_rating: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': 'Failed to submit rating', 'message': str(e)}), 500

@bp.route('/user', methods=['GET'])
@token_required
def get_user_ratings():
    """Get all ratings by current user"""
    query = """
        SELECT rat.rating_id, rat.restaurant_id, r.name, rat.rating_value, rat.rating_date
        FROM RATINGS rat
        JOIN RESTAURANTS r ON rat.restaurant_id = r.restaurant_id
        WHERE rat.user_id = :user_id
        ORDER BY rat.rating_date DESC
    """
    
    ratings = db.execute_query(query, {'user_id': request.user_id})
    
    if ratings is None:
        return jsonify({'error': 'Database query failed'}), 500
    
    result = []
    for r in ratings:
        result.append({
            'rating_id': r['rating_id'],
            'restaurant_id': r['restaurant_id'],
            'restaurant_name': r['name'],
            'rating_value': float(r['rating_value']),
            'rating_date': r['rating_date'].strftime('%Y-%m-%d') if r.get('rating_date') else None
        })
    
    return jsonify(result), 200
from flask import Blueprint, request, jsonify
from app.database import db
from app.utils.auth_helpers import token_required
import uuid

bp = Blueprint('reviews', __name__)

@bp.route('/restaurant/<restaurant_id>', methods=['GET'])
def get_reviews(restaurant_id):
    """Get reviews for a restaurant"""
    query = """
        SELECT r.review_id, r.user_id, u.username, r.review_text,
               r.review_date, r.helpful_count
        FROM REVIEWS r
        JOIN USERS u ON r.user_id = u.user_id
        WHERE r.restaurant_id = :restaurant_id
        ORDER BY r.review_date DESC
    """
    
    reviews = db.execute_query(query, {'restaurant_id': restaurant_id})
    
    if reviews is None:
        return jsonify({'error': 'Database query failed'}), 500
    
    result = []
    for r in reviews:
        result.append({
            'review_id': r['review_id'],
            'user_id': r['user_id'],
            'username': r['username'],
            'review_text': r['review_text'],
            'review_date': r['review_date'].strftime('%Y-%m-%d') if r.get('review_date') else None,
            'helpful_count': int(r.get('helpful_count', 0))
        })
    
    return jsonify(result), 200

@bp.route('/', methods=['POST'])
@token_required
def create_review():
    """Create a new review"""
    data = request.get_json()
    
    if not data.get('restaurant_id') or not data.get('review_text'):
        return jsonify({'error': 'Restaurant ID and review text are required'}), 400
    
    review_id = f"REV{uuid.uuid4().hex[:8].upper()}"
    
    result = db.execute_non_query(
        """INSERT INTO REVIEWS (review_id, user_id, restaurant_id, review_text)
           VALUES (:review_id, :user_id, :restaurant_id, :review_text)""",
        {
            'review_id': review_id,
            'user_id': request.user_id,
            'restaurant_id': data['restaurant_id'],
            'review_text': data['review_text']
        }
    )
    
    success = result is not None and result.get('rowcount', 0) > 0
    
    if success:
        return jsonify({'message': 'Review created successfully', 'review_id': review_id}), 201
    else:
        return jsonify({'error': 'Failed to create review'}), 500
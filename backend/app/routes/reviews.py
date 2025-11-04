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
        WHERE r.restaurant_id = :1
        ORDER BY r.review_date DESC
    """
    
    reviews = db.execute_query(query, (restaurant_id,))
    
    result = []
    for r in reviews:
        result.append({
            'review_id': r[0],
            'user_id': r[1],
            'username': r[2],
            'review_text': r[3],
            'review_date': r[4].strftime('%Y-%m-%d') if r[4] else None,
            'helpful_count': r[5]
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
    
    success = db.execute_update(
        """INSERT INTO REVIEWS (review_id, user_id, restaurant_id, review_text)
           VALUES (:1, :2, :3, :4)""",
        (review_id, request.user_id, data['restaurant_id'], data['review_text'])
    )
    
    if success:
        return jsonify({'message': 'Review created successfully', 'review_id': review_id}), 201
    else:
        return jsonify({'error': 'Failed to create review'}), 500
from flask import Blueprint, request, jsonify
from app.database import db
from app.utils.auth_helpers import token_required
import uuid
import traceback

bp = Blueprint('reviews', __name__)

@bp.route('/restaurant/<restaurant_id>', methods=['GET'])
def get_reviews(restaurant_id):
    """Get reviews for a restaurant"""
    try:
        query = """
            SELECT r.review_id, r.user_id, u.username, 
                   TO_CHAR(r.review_text) as review_text,
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
    except Exception as e:
        print(f"ERROR in get_reviews: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch reviews'}), 500

@bp.route('/', methods=['POST'])
@token_required
def create_review():
    """Create a new review"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if not data.get('restaurant_id') or not data.get('review_text'):
            return jsonify({'error': 'Restaurant ID and review text are required'}), 400
        
        # Check if user already reviewed this restaurant
        existing = db.execute_query(
            "SELECT review_id FROM REVIEWS WHERE user_id = :user_id AND restaurant_id = :restaurant_id",
            {'user_id': request.user_id, 'restaurant_id': data['restaurant_id']},
            fetch_one=True
        )
        
        if existing:
            # Update existing review
            result = db.execute_non_query(
                """UPDATE REVIEWS 
                   SET review_text = :review_text, review_date = SYSDATE 
                   WHERE review_id = :review_id""",
                {'review_text': data['review_text'], 'review_id': existing['review_id']}
            )
            message = 'Review updated successfully'
            review_id = existing['review_id']
        else:
            # Create new review
            review_id = f"REV{uuid.uuid4().hex[:8].upper()}"
            result = db.execute_non_query(
                """INSERT INTO REVIEWS (review_id, user_id, restaurant_id, review_text, review_date)
                   VALUES (:review_id, :user_id, :restaurant_id, :review_text, SYSDATE)""",
                {
                    'review_id': review_id,
                    'user_id': request.user_id,
                    'restaurant_id': data['restaurant_id'],
                    'review_text': data['review_text']
                }
            )
            message = 'Review created successfully'
        
        success = result is not None and result.get('rowcount', 0) > 0
        
        if success:
            return jsonify({
                'message': message,
                'review_id': review_id
            }), 201
        else:
            return jsonify({'error': 'Failed to create review'}), 500
            
    except Exception as e:
        print(f"ERROR in create_review: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to create review', 'message': str(e)}), 500

@bp.route('/user', methods=['GET'])
@token_required
def get_user_reviews():
    """Get all reviews by current user"""
    try:
        query = """
            SELECT r.review_id, r.restaurant_id, rest.name as restaurant_name,
                   TO_CHAR(r.review_text) as review_text,
                   r.review_date, r.helpful_count
            FROM REVIEWS r
            JOIN RESTAURANTS rest ON r.restaurant_id = rest.restaurant_id
            WHERE r.user_id = :user_id
            ORDER BY r.review_date DESC
        """
        
        reviews = db.execute_query(query, {'user_id': request.user_id})
        
        if reviews is None:
            return jsonify({'error': 'Database query failed'}), 500
        
        result = []
        for r in reviews:
            result.append({
                'review_id': r['review_id'],
                'restaurant_id': r['restaurant_id'],
                'restaurant_name': r['restaurant_name'],
                'review_text': r['review_text'],
                'review_date': r['review_date'].strftime('%Y-%m-%d') if r.get('review_date') else None,
                'helpful_count': int(r.get('helpful_count', 0))
            })
        
        return jsonify(result), 200
    except Exception as e:
        print(f"ERROR in get_user_reviews: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch reviews'}), 500

@bp.route('/<review_id>/helpful', methods=['POST'])
@token_required
def mark_helpful(review_id):
    """Mark a review as helpful"""
    try:
        result = db.execute_non_query(
            """UPDATE REVIEWS 
               SET helpful_count = helpful_count + 1 
               WHERE review_id = :review_id""",
            {'review_id': review_id}
        )
        
        if result and result.get('rowcount', 0) > 0:
            return jsonify({'message': 'Marked as helpful'}), 200
        else:
            return jsonify({'error': 'Review not found'}), 404
            
    except Exception as e:
        print(f"ERROR in mark_helpful: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to mark helpful'}), 500
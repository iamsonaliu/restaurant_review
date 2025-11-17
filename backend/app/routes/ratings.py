from flask import Blueprint, request, jsonify
from app.database import db
from app.utils.auth_helpers import token_required
import uuid
import traceback

bp = Blueprint('ratings', __name__)

@bp.route('/', methods=['POST'])
@token_required
def create_rating():
    """Create or update rating"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        if not data.get('restaurant_id') or not data.get('rating_value'):
            return jsonify({'error': 'Restaurant ID and rating value are required'}), 400
        
        rating_value = float(data['rating_value'])
        if not (1 <= rating_value <= 5):
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        # Check if user already rated
        existing = db.execute_query(
            "SELECT rating_id FROM RATINGS WHERE user_id = :user_id AND restaurant_id = :restaurant_id",
            {'user_id': request.user_id, 'restaurant_id': data['restaurant_id']},
            fetch_one=True
        )
        
        if existing:
            # Update existing rating
            result = db.execute_non_query(
                """UPDATE RATINGS 
                   SET rating_value = :rating_value, rating_date = SYSDATE 
                   WHERE rating_id = :rating_id""",
                {'rating_value': rating_value, 'rating_id': existing['rating_id']}
            )
            message = 'Rating updated successfully'
            rating_id = existing['rating_id']
        else:
            # Create new rating
            rating_id = f"RAT{uuid.uuid4().hex[:8].upper()}"
            result = db.execute_non_query(
                """INSERT INTO RATINGS (rating_id, user_id, restaurant_id, rating_value, rating_date)
                   VALUES (:rating_id, :user_id, :restaurant_id, :rating_value, SYSDATE)""",
                {
                    'rating_id': rating_id,
                    'user_id': request.user_id,
                    'restaurant_id': data['restaurant_id'],
                    'rating_value': rating_value
                }
            )
            message = 'Rating created successfully'
        
        if result and result.get('rowcount', 0) > 0:
            # Manually trigger average rating update
            update_avg_rating(data['restaurant_id'])
            
            return jsonify({
                'message': message,
                'rating_id': rating_id,
                'rating_value': rating_value
            }), 201
        else:
            return jsonify({'error': 'Failed to submit rating'}), 500
            
    except Exception as e:
        print(f"ERROR in create_rating: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to submit rating', 'message': str(e)}), 500

def update_avg_rating(restaurant_id):
    """Manually update average rating for a restaurant"""
    try:
        # Calculate new average
        result = db.execute_query(
            """SELECT ROUND(AVG(rating_value), 1) as avg_rating, COUNT(*) as vote_count
               FROM RATINGS WHERE restaurant_id = :restaurant_id""",
            {'restaurant_id': restaurant_id},
            fetch_one=True
        )
        
        if result:
            avg_rating = result.get('avg_rating', 0) or 0
            vote_count = result.get('vote_count', 0) or 0
            
            # Update restaurant
            db.execute_non_query(
                """UPDATE RESTAURANTS 
                   SET avg_rating = :avg_rating, votes = :votes 
                   WHERE restaurant_id = :restaurant_id""",
                {
                    'avg_rating': avg_rating,
                    'votes': vote_count,
                    'restaurant_id': restaurant_id
                }
            )
            print(f"Updated avg_rating for {restaurant_id}: {avg_rating} ({vote_count} votes)")
    except Exception as e:
        print(f"Error updating avg_rating: {e}")

@bp.route('/user', methods=['GET'])
@token_required
def get_user_ratings():
    """Get all ratings by current user"""
    try:
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
    except Exception as e:
        print(f"ERROR in get_user_ratings: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch ratings', 'message': str(e)}), 500

@bp.route('/restaurant/<restaurant_id>', methods=['GET'])
def get_restaurant_ratings(restaurant_id):
    """Get rating statistics for a restaurant"""
    try:
        query = """
            SELECT 
                COUNT(*) as total_ratings,
                ROUND(AVG(rating_value), 1) as avg_rating,
                COUNT(CASE WHEN rating_value = 5 THEN 1 END) as five_star,
                COUNT(CASE WHEN rating_value = 4 THEN 1 END) as four_star,
                COUNT(CASE WHEN rating_value = 3 THEN 1 END) as three_star,
                COUNT(CASE WHEN rating_value = 2 THEN 1 END) as two_star,
                COUNT(CASE WHEN rating_value = 1 THEN 1 END) as one_star
            FROM RATINGS
            WHERE restaurant_id = :restaurant_id
        """
        
        stats = db.execute_query(query, {'restaurant_id': restaurant_id}, fetch_one=True)
        
        if stats:
            return jsonify({
                'total_ratings': int(stats.get('total_ratings', 0)),
                'avg_rating': float(stats.get('avg_rating', 0)) if stats.get('avg_rating') else 0,
                'distribution': {
                    '5': int(stats.get('five_star', 0)),
                    '4': int(stats.get('four_star', 0)),
                    '3': int(stats.get('three_star', 0)),
                    '2': int(stats.get('two_star', 0)),
                    '1': int(stats.get('one_star', 0))
                }
            }), 200
        else:
            return jsonify({
                'total_ratings': 0,
                'avg_rating': 0,
                'distribution': {'5': 0, '4': 0, '3': 0, '2': 0, '1': 0}
            }), 200
            
    except Exception as e:
        print(f"ERROR in get_restaurant_ratings: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch rating stats'}), 500
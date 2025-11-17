from flask import Blueprint, request, jsonify
from app.database import db
from app.utils.auth_helpers import token_required
import traceback
import json

bp = Blueprint('profile', __name__)

@bp.route('/', methods=['GET'])
@token_required
def get_profile():
    """Get user profile with stats"""
    try:
        # Get user info
        user = db.execute_query(
            """SELECT user_id, username, email, registration_date, role
               FROM USERS WHERE user_id = :user_id""",
            {'user_id': request.user_id},
            fetch_one=True
        )
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get ratings count
        ratings_count = db.execute_query(
            "SELECT COUNT(*) as count FROM RATINGS WHERE user_id = :user_id",
            {'user_id': request.user_id},
            fetch_one=True
        )
        
        # Get reviews count
        reviews_count = db.execute_query(
            "SELECT COUNT(*) as count FROM REVIEWS WHERE user_id = :user_id",
            {'user_id': request.user_id},
            fetch_one=True
        )
        
        # Get favorite city (most rated city)
        favorite_city = db.execute_query(
            """SELECT r.city, COUNT(*) as count
               FROM RATINGS rat
               JOIN RESTAURANTS r ON rat.restaurant_id = r.restaurant_id
               WHERE rat.user_id = :user_id
               GROUP BY r.city
               ORDER BY count DESC""",
            {'user_id': request.user_id},
            fetch_one=True
        )
        
        # Get preferences (if exists in a user_preferences table)
        # For now, we'll use a simple approach
        
        return jsonify({
            'user_id': user['user_id'],
            'username': user['username'],
            'email': user['email'],
            'registration_date': user['registration_date'].strftime('%Y-%m-%d') if user.get('registration_date') else None,
            'role': user.get('role', 'user'),
            'stats': {
                'ratings_count': ratings_count['count'] if ratings_count else 0,
                'reviews_count': reviews_count['count'] if reviews_count else 0,
                'favorite_city': favorite_city['city'] if favorite_city else 'Dehradun'
            }
        }), 200
        
    except Exception as e:
        print(f"ERROR in get_profile: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch profile'}), 500

@bp.route('/', methods=['PUT'])
@token_required
def update_profile():
    """Update user profile"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update allowed fields
        update_fields = []
        params = {'user_id': request.user_id}
        
        if 'username' in data:
            update_fields.append("username = :username")
            params['username'] = data['username']
        
        if 'email' in data:
            # Check if email is already taken by another user
            existing = db.execute_query(
                "SELECT user_id FROM USERS WHERE email = :email AND user_id != :user_id",
                {'email': data['email'], 'user_id': request.user_id},
                fetch_one=True
            )
            if existing:
                return jsonify({'error': 'Email already in use'}), 400
            
            update_fields.append("email = :email")
            params['email'] = data['email']
        
        if not update_fields:
            return jsonify({'error': 'No valid fields to update'}), 400
        
        query = f"UPDATE USERS SET {', '.join(update_fields)} WHERE user_id = :user_id"
        result = db.execute_non_query(query, params)
        
        if result and result.get('rowcount', 0) > 0:
            # Get updated user
            user = db.execute_query(
                "SELECT user_id, username, email FROM USERS WHERE user_id = :user_id",
                {'user_id': request.user_id},
                fetch_one=True
            )
            
            return jsonify({
                'message': 'Profile updated successfully',
                'user': {
                    'user_id': user['user_id'],
                    'username': user['username'],
                    'email': user['email']
                }
            }), 200
        else:
            return jsonify({'error': 'Failed to update profile'}), 500
            
    except Exception as e:
        print(f"ERROR in update_profile: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to update profile', 'message': str(e)}), 500

@bp.route('/activity', methods=['GET'])
@token_required
def get_activity():
    """Get user's recent activity"""
    try:
        # Get recent ratings
        ratings = db.execute_query(
            """SELECT rat.rating_id, rat.restaurant_id, r.name, rat.rating_value, rat.rating_date
               FROM RATINGS rat
               JOIN RESTAURANTS r ON rat.restaurant_id = r.restaurant_id
               WHERE rat.user_id = :user_id
               ORDER BY rat.rating_date DESC""",
            {'user_id': request.user_id}
        )
        
        # Get recent reviews
        reviews = db.execute_query(
            """SELECT rev.review_id, rev.restaurant_id, r.name, 
                      TO_CHAR(rev.review_text) as review_text, rev.review_date
               FROM REVIEWS rev
               JOIN RESTAURANTS r ON rev.restaurant_id = r.restaurant_id
               WHERE rev.user_id = :user_id
               ORDER BY rev.review_date DESC""",
            {'user_id': request.user_id}
        )
        
        return jsonify({
            'ratings': [
                {
                    'rating_id': r['rating_id'],
                    'restaurant_id': r['restaurant_id'],
                    'restaurant_name': r['name'],
                    'rating_value': float(r['rating_value']),
                    'rating_date': r['rating_date'].strftime('%Y-%m-%d') if r.get('rating_date') else None
                }
                for r in (ratings or [])
            ],
            'reviews': [
                {
                    'review_id': r['review_id'],
                    'restaurant_id': r['restaurant_id'],
                    'restaurant_name': r['name'],
                    'review_text': r['review_text'],
                    'review_date': r['review_date'].strftime('%Y-%m-%d') if r.get('review_date') else None
                }
                for r in (reviews or [])
            ]
        }), 200
        
    except Exception as e:
        print(f"ERROR in get_activity: {e}")
        traceback.print_exc()
        return jsonify({'error': 'Failed to fetch activity'}), 500
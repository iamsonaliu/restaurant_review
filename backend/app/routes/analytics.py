from flask import Blueprint, jsonify
from app.database import db

bp = Blueprint('analytics', __name__)

@bp.route('/top-rated', methods=['GET'])
def top_rated():
    """Get top rated restaurants"""
    query = """
        SELECT restaurant_id, name, city, avg_rating, votes
        FROM RESTAURANTS
        WHERE votes >= 5
        ORDER BY avg_rating DESC, votes DESC
        FETCH FIRST 10 ROWS ONLY
    """
    
    restaurants = db.execute_query(query)
    
    result = []
    for r in restaurants:
        result.append({
            'restaurant_id': r[0],
            'name': r[1],
            'city': r[2],
            'avg_rating': float(r[3]),
            'votes': r[4]
        })
    
    return jsonify(result), 200

@bp.route('/city-stats', methods=['GET'])
def city_stats():
    """Get statistics by city"""
    query = """
        SELECT city, 
               COUNT(*) as total_restaurants,
               ROUND(AVG(avg_rating), 2) as avg_city_rating,
               SUM(votes) as total_votes
        FROM RESTAURANTS
        GROUP BY city
        ORDER BY city
    """
    
    stats = db.execute_query(query)
    
    result = []
    for s in stats:
        result.append({
            'city': s[0],
            'total_restaurants': s[1],
            'avg_rating': float(s[2]) if s[2] else 0,
            'total_votes': s[3]
        })
    
    return jsonify(result), 200
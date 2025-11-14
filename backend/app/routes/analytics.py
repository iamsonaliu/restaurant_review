from flask import Blueprint, jsonify
from app.database import db

bp = Blueprint('analytics', __name__)

@bp.route('/top-rated', methods=['GET'])
def top_rated():
    """Get top rated restaurants"""
    try:
        # Use ROWNUM for Oracle 11g compatibility
        query = """
            SELECT * FROM (
                SELECT restaurant_id, name, city, avg_rating, votes
                FROM RESTAURANTS
                WHERE votes >= 4
                ORDER BY avg_rating DESC, votes DESC
            ) WHERE ROWNUM <= 10
        """
        
        restaurants = db.execute_query(query)
        
        if restaurants is None:
            print("ERROR: top_rated query returned None")
            return jsonify({'error': 'Database query failed'}), 500
        
        if not isinstance(restaurants, list):
            print(f"ERROR: Expected list, got {type(restaurants)}")
            return jsonify({'error': 'Database query failed', 'message': 'Invalid data format'}), 500
    except Exception as query_error:
        print(f"ERROR in top_rated query: {query_error}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'error': 'Database query failed',
            'message': f'Query execution error: {str(query_error)}'
        }), 500
    
    result = []
    for r in restaurants:
        result.append({
            'restaurant_id': r['restaurant_id'],
            'name': r['name'],
            'city': r['city'],
            'avg_rating': float(r['avg_rating']) if r.get('avg_rating') else 0,
            'votes': int(r['votes']) if r.get('votes') else 0
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
    
    if stats is None:
        return jsonify({'error': 'Database query failed'}), 500
    
    result = []
    for s in stats:
        result.append({
            'city': s['city'],
            'total_restaurants': int(s['total_restaurants']) if s.get('total_restaurants') else 0,
            'avg_rating': float(s['avg_city_rating']) if s.get('avg_city_rating') else 0,
            'total_votes': int(s['total_votes']) if s.get('total_votes') else 0
        })
    
    return jsonify(result), 200
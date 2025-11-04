from flask import Blueprint, request, jsonify
from app.database import db

bp = Blueprint('restaurants', __name__)

@bp.route('/', methods=['GET'])
def get_restaurants():
    """Get all restaurants with filters"""
    city = request.args.get('city')
    cuisine = request.args.get('cuisine')
    min_rating = request.args.get('min_rating', 0)
    search = request.args.get('search', '')
    limit = request.args.get('limit', 50)
    
    query = """
        SELECT DISTINCT
            r.restaurant_id, r.name, r.address, r.city, r.region,
            r.phone_number, r.website_url, r.avg_rating, r.price_range,
            r.dining_type, r.timings, r.votes, r.rating_type
        FROM RESTAURANTS r
        LEFT JOIN RESTAURANT_CATEGORIES rc ON r.restaurant_id = rc.restaurant_id
        LEFT JOIN CATEGORIES c ON rc.category_id = c.category_id
        WHERE 1=1
    """
    
    params = []
    
    if city:
        query += " AND r.city = :city"
        params.append(city)
    
    if cuisine:
        query += " AND c.category_name = :cuisine"
        params.append(cuisine)
    
    if search:
        query += " AND LOWER(r.name) LIKE LOWER(:search)"
        params.append(f'%{search}%')
    
    query += " AND r.avg_rating >= :min_rating"
    params.append(min_rating)
    
    query += " ORDER BY r.avg_rating DESC, r.votes DESC"
    query += f" FETCH FIRST {limit} ROWS ONLY"
    
    restaurants = db.execute_query(query, params if params else None)
    
    result = []
    for r in restaurants:
        # Get cuisines for this restaurant
        cuisines_query = """
            SELECT c.category_name
            FROM CATEGORIES c
            JOIN RESTAURANT_CATEGORIES rc ON c.category_id = rc.category_id
            WHERE rc.restaurant_id = :1
        """
        cuisines = db.execute_query(cuisines_query, (r[0],))
        
        result.append({
            'restaurant_id': r[0],
            'name': r[1],
            'address': r[2],
            'city': r[3],
            'region': r[4],
            'phone_number': r[5],
            'website_url': r[6],
            'avg_rating': float(r[7]) if r[7] else 0,
            'price_range': r[8],
            'dining_type': r[9],
            'timings': r[10],
            'votes': r[11],
            'rating_type': r[12],
            'cuisines': [c[0] for c in cuisines]
        })
    
    return jsonify(result), 200

@bp.route('/<restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    """Get single restaurant details"""
    query = """
        SELECT r.restaurant_id, r.name, r.address, r.city, r.region,
               r.phone_number, r.website_url, r.avg_rating, r.price_range,
               r.dining_type, r.timings, r.votes, r.rating_type
        FROM RESTAURANTS r
        WHERE r.restaurant_id = :1
    """
    
    restaurant = db.execute_query(query, (restaurant_id,), fetch_one=True)
    
    if not restaurant:
        return jsonify({'error': 'Restaurant not found'}), 404
    
    # Get cuisines
    cuisines_query = """
        SELECT c.category_name
        FROM CATEGORIES c
        JOIN RESTAURANT_CATEGORIES rc ON c.category_id = rc.category_id
        WHERE rc.restaurant_id = :1
    """
    cuisines = db.execute_query(cuisines_query, (restaurant_id,))
    
    result = {
        'restaurant_id': restaurant[0],
        'name': restaurant[1],
        'address': restaurant[2],
        'city': restaurant[3],
        'region': restaurant[4],
        'phone_number': restaurant[5],
        'website_url': restaurant[6],
        'avg_rating': float(restaurant[7]) if restaurant[7] else 0,
        'price_range': restaurant[8],
        'dining_type': restaurant[9],
        'timings': restaurant[10],
        'votes': restaurant[11],
        'rating_type': restaurant[12],
        'cuisines': [c[0] for c in cuisines]
    }
    
    return jsonify(result), 200

@bp.route('/cities', methods=['GET'])
def get_cities():
    """Get list of cities"""
    query = """
        SELECT DISTINCT city, COUNT(*) as restaurant_count
        FROM RESTAURANTS
        GROUP BY city
        ORDER BY city
    """
    cities = db.execute_query(query)
    
    result = [{'city': c[0], 'count': c[1]} for c in cities]
    return jsonify(result), 200

@bp.route('/categories', methods=['GET'])
def get_categories():
    """Get list of cuisines"""
    query = """
        SELECT category_id, category_name
        FROM CATEGORIES
        ORDER BY category_name
    """
    categories = db.execute_query(query)
    
    result = [{'id': c[0], 'name': c[1]} for c in categories]
    return jsonify(result), 200
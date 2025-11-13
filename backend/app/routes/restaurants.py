from flask import Blueprint, request, jsonify
from app.database import db

bp = Blueprint('restaurants', __name__)

@bp.route('/', methods=['GET'])
def get_restaurants():
    """Get all restaurants with filters"""
    try:
        city = request.args.get('city')
        cuisine = request.args.get('cuisine')
        min_rating = request.args.get('min_rating', 0)
        search = request.args.get('search', '')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Build dynamic query
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
        
        params = {}
        param_counter = 1
        
        if city:
            query += f" AND r.city = :p{param_counter}"
            params[f'p{param_counter}'] = city
            param_counter += 1
        
        if cuisine:
            query += f" AND c.category_name = :p{param_counter}"
            params[f'p{param_counter}'] = cuisine
            param_counter += 1
        
        if search:
            query += f" AND LOWER(r.name) LIKE LOWER(:p{param_counter})"
            params[f'p{param_counter}'] = f'%{search}%'
            param_counter += 1
        
        query += f" AND r.avg_rating >= :p{param_counter}"
        params[f'p{param_counter}'] = float(min_rating)
        param_counter += 1
        
        query += " ORDER BY r.avg_rating DESC, r.votes DESC"
        query += f" OFFSET {offset} ROWS FETCH NEXT {limit} ROWS ONLY"
        
        restaurants = db.execute_query(query, params if params else None)
        
        if restaurants is None:
            return jsonify({'error': 'Database query failed'}), 500
        
        result = []
        for r in restaurants:
            # Get cuisines for this restaurant
            cuisines_query = """
                SELECT c.category_name
                FROM CATEGORIES c
                JOIN RESTAURANT_CATEGORIES rc ON c.category_id = rc.category_id
                WHERE rc.restaurant_id = :1
            """
            cuisines = db.execute_query(cuisines_query, [r[0]])
            
            result.append({
                'restaurant_id': r[0],
                'name': r[1],
                'address': r[2],
                'city': r[3],
                'region': r[4],
                'phone_number': r[5],
                'website_url': r[6],
                'avg_rating': float(r[7]) if r[7] else 0,
                'price_range': int(r[8]) if r[8] else 0,
                'dining_type': r[9],
                'timings': r[10],
                'votes': int(r[11]) if r[11] else 0,
                'rating_type': r[12],
                'cuisines': [c[0] for c in cuisines] if cuisines else []
            })
        
        return jsonify({
            'restaurants': result,
            'total': len(result),
            'offset': offset,
            'limit': limit
        }), 200
    
    except Exception as e:
        print(f"Error in get_restaurants: {e}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@bp.route('/<restaurant_id>', methods=['GET'])
def get_restaurant(restaurant_id):
    """Get single restaurant details"""
    try:
        query = """
            SELECT r.restaurant_id, r.name, r.address, r.city, r.region,
                   r.phone_number, r.website_url, r.avg_rating, r.price_range,
                   r.dining_type, r.timings, r.votes, r.rating_type
            FROM RESTAURANTS r
            WHERE r.restaurant_id = :1
        """
        
        restaurant = db.execute_query(query, [restaurant_id], fetch_one=True)
        
        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404
        
        # Get cuisines
        cuisines_query = """
            SELECT c.category_name
            FROM CATEGORIES c
            JOIN RESTAURANT_CATEGORIES rc ON c.category_id = rc.category_id
            WHERE rc.restaurant_id = :1
        """
        cuisines = db.execute_query(cuisines_query, [restaurant_id])
        
        # Get recent reviews count
        reviews_query = "SELECT COUNT(*) FROM REVIEWS WHERE restaurant_id = :1"
        review_count = db.execute_query(reviews_query, [restaurant_id], fetch_one=True)
        
        result = {
            'restaurant_id': restaurant[0],
            'name': restaurant[1],
            'address': restaurant[2],
            'city': restaurant[3],
            'region': restaurant[4],
            'phone_number': restaurant[5],
            'website_url': restaurant[6],
            'avg_rating': float(restaurant[7]) if restaurant[7] else 0,
            'price_range': int(restaurant[8]) if restaurant[8] else 0,
            'dining_type': restaurant[9],
            'timings': restaurant[10],
            'votes': int(restaurant[11]) if restaurant[11] else 0,
            'rating_type': restaurant[12],
            'cuisines': [c[0] for c in cuisines] if cuisines else [],
            'review_count': review_count[0] if review_count else 0
        }
        
        return jsonify(result), 200
    
    except Exception as e:
        print(f"Error in get_restaurant: {e}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@bp.route('/cities', methods=['GET'])
def get_cities():
    """Get list of cities with restaurant counts"""
    try:
        query = """
            SELECT DISTINCT city, COUNT(*) as restaurant_count
            FROM RESTAURANTS
            GROUP BY city
            ORDER BY city
        """
        cities = db.execute_query(query)
        
        if cities is None:
            return jsonify({'error': 'Database query failed'}), 500
        
        result = [{'city': c[0], 'count': int(c[1])} for c in cities]
        return jsonify(result), 200
    
    except Exception as e:
        print(f"Error in get_cities: {e}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@bp.route('/categories', methods=['GET'])
def get_categories():
    """Get list of cuisine categories"""
    try:
        query = """
            SELECT DISTINCT c.category_id, c.category_name, COUNT(rc.restaurant_id) as count
            FROM CATEGORIES c
            LEFT JOIN RESTAURANT_CATEGORIES rc ON c.category_id = rc.category_id
            GROUP BY c.category_id, c.category_name
            ORDER BY c.category_name
        """
        categories = db.execute_query(query)
        
        if categories is None:
            return jsonify({'error': 'Database query failed'}), 500
        
        result = [
            {
                'id': c[0], 
                'name': c[1],
                'count': int(c[2]) if c[2] else 0
            } 
            for c in categories
        ]
        return jsonify(result), 200
    
    except Exception as e:
        print(f"Error in get_categories: {e}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500

@bp.route('/search', methods=['GET'])
def search_restaurants():
    """Advanced search endpoint"""
    try:
        query_text = request.args.get('q', '')
        city = request.args.get('city')
        min_rating = float(request.args.get('min_rating', 0))
        max_price = request.args.get('max_price')
        cuisine = request.args.get('cuisine')
        
        query = """
            SELECT DISTINCT r.restaurant_id, r.name, r.city, r.avg_rating, 
                   r.price_range, r.votes, r.dining_type
            FROM RESTAURANTS r
            LEFT JOIN RESTAURANT_CATEGORIES rc ON r.restaurant_id = rc.restaurant_id
            LEFT JOIN CATEGORIES c ON rc.category_id = c.category_id
            WHERE r.avg_rating >= :min_rating
        """
        
        params = {'min_rating': min_rating}
        
        if query_text:
            query += " AND LOWER(r.name) LIKE LOWER(:query)"
            params['query'] = f'%{query_text}%'
        
        if city:
            query += " AND r.city = :city"
            params['city'] = city
        
        if max_price:
            query += " AND r.price_range <= :max_price"
            params['max_price'] = int(max_price)
        
        if cuisine:
            query += " AND c.category_name = :cuisine"
            params['cuisine'] = cuisine
        
        query += " ORDER BY r.avg_rating DESC, r.votes DESC FETCH FIRST 20 ROWS ONLY"
        
        results = db.execute_query(query, params)
        
        if results is None:
            return jsonify({'error': 'Database query failed'}), 500
        
        restaurants = [
            {
                'restaurant_id': r[0],
                'name': r[1],
                'city': r[2],
                'avg_rating': float(r[3]) if r[3] else 0,
                'price_range': int(r[4]) if r[4] else 0,
                'votes': int(r[5]) if r[5] else 0,
                'dining_type': r[6]
            }
            for r in results
        ]
        
        return jsonify({
            'results': restaurants,
            'count': len(restaurants)
        }), 200
    
    except Exception as e:
        print(f"Error in search_restaurants: {e}")
        return jsonify({'error': 'Internal server error', 'message': str(e)}), 500
from flask import Blueprint, request, jsonify
from app.database import db

bp = Blueprint('restaurants', __name__)

@bp.route('/', methods=['GET'])
@bp.route('', methods=['GET'])  # Handle both with and without trailing slash
def get_restaurants():
    """Get all restaurants with filters"""
    try:
        city = request.args.get('city')
        cuisine = request.args.get('cuisine')
        min_rating = float(request.args.get('min_rating', 0) or 0)
        search = request.args.get('search', '')
        limit = int(request.args.get('limit', 50) or 50)
        offset = int(request.args.get('offset', 0) or 0)
        
        # Build dynamic query - use subquery to avoid DISTINCT issues with JOINs
        base_query = """
            SELECT r.restaurant_id, r.name, r.address, r.city, r.region,
                   r.phone_number, r.website_url, r.avg_rating, r.price_range,
                   r.dining_type, r.timings, r.votes, r.rating_type
            FROM RESTAURANTS r
            WHERE r.avg_rating >= :min_rating
        """
        
        params = {'min_rating': min_rating}
        
        if city:
            base_query += " AND r.city = :city"
            params['city'] = city
        
        if search:
            base_query += " AND LOWER(r.name) LIKE LOWER(:search)"
            params['search'] = f'%{search}%'
        
        # If cuisine filter, need to join with categories
        if cuisine:
            base_query = """
                SELECT DISTINCT r.restaurant_id, r.name, r.address, r.city, r.region,
                       r.phone_number, r.website_url, r.avg_rating, r.price_range,
                       r.dining_type, r.timings, r.votes, r.rating_type
                FROM RESTAURANTS r
                INNER JOIN RESTAURANT_CATEGORIES rc ON r.restaurant_id = rc.restaurant_id
                INNER JOIN CATEGORIES c ON rc.category_id = c.category_id
                WHERE r.avg_rating >= :min_rating
                AND c.category_name = :cuisine
            """
            if city:
                base_query += " AND r.city = :city"
            if search:
                base_query += " AND LOWER(r.name) LIKE LOWER(:search)"
        
        # Use ROWNUM for Oracle 11g compatibility (instead of OFFSET/FETCH)
        # Wrap base_query in subquery for proper ROWNUM pagination
        query = f"""
            SELECT restaurant_id, name, address, city, region,
                   phone_number, website_url, avg_rating, price_range,
                   dining_type, timings, votes, rating_type
            FROM (
                SELECT inner.*, ROWNUM rnum FROM (
                    {base_query}
                    ORDER BY avg_rating DESC, votes DESC
                ) inner WHERE ROWNUM <= {offset + limit}
            ) outer WHERE rnum > {offset}
        """
        
        try:
            restaurants = db.execute_query(query, params)
        except Exception as query_error:
            print(f"ERROR in get_restaurants query: {query_error}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'error': 'Database query failed', 
                'message': f'Query execution error: {str(query_error)}'
            }), 500
        
        if restaurants is None:
            print("ERROR: Database query returned None")
            return jsonify({'error': 'Database query failed', 'message': 'Unable to fetch restaurants from database'}), 500
        
        if not isinstance(restaurants, list):
            print(f"ERROR: Expected list, got {type(restaurants)}")
            return jsonify({'error': 'Database query failed', 'message': 'Invalid data format from database'}), 500
        
        result = []
        for r in restaurants:
            try:
                # Get cuisines for this restaurant
                cuisines_query = """
                    SELECT c.category_name
                    FROM CATEGORIES c
                    JOIN RESTAURANT_CATEGORIES rc ON c.category_id = rc.category_id
                    WHERE rc.restaurant_id = :restaurant_id
                """
                cuisines = db.execute_query(cuisines_query, {'restaurant_id': r['restaurant_id']})
                
                result.append({
                    'restaurant_id': r['restaurant_id'],
                    'name': r['name'],
                    'address': r.get('address'),
                    'city': r.get('city'),
                    'region': r.get('region'),
                    'phone_number': r.get('phone_number'),
                    'website_url': r.get('website_url'),
                    'avg_rating': float(r['avg_rating']) if r.get('avg_rating') is not None else 0.0,
                    'price_range': int(r['price_range']) if r.get('price_range') is not None else 0,
                    'dining_type': r.get('dining_type'),
                    'timings': r.get('timings'),
                    'votes': int(r['votes']) if r.get('votes') is not None else 0,
                    'rating_type': r.get('rating_type'),
                    'cuisines': [c['category_name'] for c in cuisines] if cuisines else []
                })
            except Exception as e:
                print(f"Error processing restaurant {r.get('restaurant_id', 'unknown')}: {e}")
                import traceback
                traceback.print_exc()
                continue
        
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
            WHERE r.restaurant_id = :restaurant_id
        """
        
        restaurant = db.execute_query(query, {'restaurant_id': restaurant_id}, fetch_one=True)
        
        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404
        
        # Get cuisines
        cuisines_query = """
            SELECT c.category_name
            FROM CATEGORIES c
            JOIN RESTAURANT_CATEGORIES rc ON c.category_id = rc.category_id
            WHERE rc.restaurant_id = :restaurant_id
        """
        cuisines = db.execute_query(cuisines_query, {'restaurant_id': restaurant_id})
        
        # Get recent reviews count
        reviews_query = "SELECT COUNT(*) as count FROM REVIEWS WHERE restaurant_id = :restaurant_id"
        review_count = db.execute_query(reviews_query, {'restaurant_id': restaurant_id}, fetch_one=True)
        
        result = {
            'restaurant_id': restaurant['restaurant_id'],
            'name': restaurant['name'],
            'address': restaurant.get('address'),
            'city': restaurant.get('city'),
            'region': restaurant.get('region'),
            'phone_number': restaurant.get('phone_number'),
            'website_url': restaurant.get('website_url'),
            'avg_rating': float(restaurant['avg_rating']) if restaurant.get('avg_rating') else 0,
            'price_range': int(restaurant['price_range']) if restaurant.get('price_range') else 0,
            'dining_type': restaurant.get('dining_type'),
            'timings': restaurant.get('timings'),
            'votes': int(restaurant['votes']) if restaurant.get('votes') else 0,
            'rating_type': restaurant.get('rating_type'),
            'cuisines': [c['category_name'] for c in cuisines] if cuisines else [],
            'review_count': int(review_count['count']) if review_count and review_count.get('count') else 0
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
        
        result = [{'city': c['city'], 'count': int(c['restaurant_count'])} for c in cities]
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
                'id': c['category_id'], 
                'name': c['category_name'],
                'count': int(c['count']) if c.get('count') else 0
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
        
        # Build base query without cuisine filter first
        base_query = """
            SELECT r.restaurant_id, r.name, r.city, r.avg_rating, 
                   r.price_range, r.votes, r.dining_type
            FROM RESTAURANTS r
            WHERE r.avg_rating >= :min_rating
        """
        
        params = {'min_rating': min_rating}
        
        if query_text:
            base_query += " AND LOWER(r.name) LIKE LOWER(:query)"
            params['query'] = f'%{query_text}%'
        
        if city:
            base_query += " AND r.city = :city"
            params['city'] = city
        
        if max_price:
            base_query += " AND r.price_range <= :max_price"
            params['max_price'] = int(max_price)
        
        # If cuisine filter, need to join with categories
        if cuisine:
            base_query = """
                SELECT DISTINCT r.restaurant_id, r.name, r.city, r.avg_rating, 
                       r.price_range, r.votes, r.dining_type
                FROM RESTAURANTS r
                INNER JOIN RESTAURANT_CATEGORIES rc ON r.restaurant_id = rc.restaurant_id
                INNER JOIN CATEGORIES c ON rc.category_id = c.category_id
                WHERE r.avg_rating >= :min_rating
                AND c.category_name = :cuisine
            """
            if query_text:
                base_query += " AND LOWER(r.name) LIKE LOWER(:query)"
            if city:
                base_query += " AND r.city = :city"
            if max_price:
                base_query += " AND r.price_range <= :max_price"
        
        # Use ROWNUM for Oracle 11g compatibility
        query = f"""
            SELECT restaurant_id, name, city, avg_rating, 
                   price_range, votes, dining_type
            FROM (
                SELECT inner.*, ROWNUM rnum FROM (
                    {base_query}
                    ORDER BY avg_rating DESC, votes DESC
                ) inner WHERE ROWNUM <= 20
            ) outer WHERE rnum > 0
        """
        
        try:
            results = db.execute_query(query, params)
        except Exception as query_error:
            print(f"ERROR in search_restaurants query: {query_error}")
            print(f"Query: {query}")
            print(f"Params: {params}")
            import traceback
            traceback.print_exc()
            return jsonify({
                'error': 'Database query failed',
                'message': f'Query execution error: {str(query_error)}'
            }), 500
        
        if results is None:
            return jsonify({'error': 'Database query failed'}), 500
        
        restaurants = [
            {
                'restaurant_id': r['restaurant_id'],
                'name': r['name'],
                'city': r['city'],
                'avg_rating': float(r['avg_rating']) if r.get('avg_rating') else 0,
                'price_range': int(r['price_range']) if r.get('price_range') else 0,
                'votes': int(r['votes']) if r.get('votes') else 0,
                'dining_type': r.get('dining_type')
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
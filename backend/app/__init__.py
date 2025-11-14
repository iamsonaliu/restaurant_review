from flask import Flask, jsonify
from flask_cors import CORS
from app.config import Config
from app.database import db
import traceback

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS with more detailed configuration
    CORS(app, 
         resources={r"/api/*": {
             "origins": app.config['CORS_ORIGINS'],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
             "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
             "expose_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "max_age": 3600
         }},
         allow_headers=["Content-Type", "Authorization", "X-Requested-With"],
         supports_credentials=True)
    
    # Connect to database
    print("\n🔌 Initializing database connection...")
    if db.connect():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
        print("⚠️  API will start but database operations will fail")
    
    # Register blueprints
    try:
        from app.routes import auth, restaurants, reviews, ratings, analytics
        
        app.register_blueprint(auth.bp, url_prefix='/api/auth')
        app.register_blueprint(restaurants.bp, url_prefix='/api/restaurants')
        app.register_blueprint(reviews.bp, url_prefix='/api/reviews')
        app.register_blueprint(ratings.bp, url_prefix='/api/ratings')
        app.register_blueprint(analytics.bp, url_prefix='/api/analytics')
        
        print("✅ All routes registered successfully")
    except Exception as e:
        print(f"❌ Error registering routes: {e}")
        traceback.print_exc()
    
    # Health check endpoint
    @app.route('/api/health')
    def health():
        db_status = "disconnected"
        db_error = None
        
        # Check if pool exists
        if not db.pool:
            db_status = "disconnected (pool not initialized)"
        else:
            try:
                # Test database connection
                result = db.execute_query("SELECT 1 FROM DUAL", fetch_one=True)
                db_status = "connected" if result else "disconnected"
            except RuntimeError as e:
                db_status = "disconnected"
                db_error = str(e)
            except Exception as e:
                db_status = f"error: {str(e)}"
                db_error = str(e)
        
        response = {
            'status': 'ok',
            'message': 'DineWise API is running',
            'database': db_status,
            'version': '1.0.0'
        }
        
        if db_error:
            response['database_error'] = db_error
        
        return jsonify(response), 200
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'message': 'Welcome to DineWise API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'auth': '/api/auth',
                'restaurants': '/api/restaurants',
                'reviews': '/api/reviews',
                'ratings': '/api/ratings',
                'analytics': '/api/analytics'
            }
        }), 200
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'error': 'Not Found',
            'message': 'The requested endpoint does not exist'
        }), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'error': 'Internal Server Error',
            'message': 'An unexpected error occurred'
        }), 500
    
    @app.errorhandler(Exception)
    def handle_exception(e):
        print(f"Unhandled exception: {e}")
        traceback.print_exc()
        return jsonify({
            'error': 'Internal Server Error',
            'message': str(e)
        }), 500
    
    # Cleanup on shutdown
    @app.teardown_appcontext
    def shutdown_session(exception=None):
        if exception:
            print(f"Error during request: {exception}")
    
    return app
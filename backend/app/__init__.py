from flask import Flask, jsonify,request
from flask_cors import CORS
from app.config import Config
from app.database import db
import traceback

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # CRITICAL: Enable CORS BEFORE registering routes
    CORS(app, 
         resources={r"/api/*": {
             "origins": ["http://localhost:5173", "http://127.0.0.1:5173"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True
         }})
    
    # Connect to database
    print("\n🔌 Initializing database connection...")
    if db.connect():
        print("✅ Database connection successful")
    else:
        print("❌ Database connection failed")
    
    # Register blueprints
    try:
        from app.routes import auth, restaurants, reviews, ratings, analytics
        
        # Try to import profile, but don't fail if it doesn't exist
        try:
            from app.routes import profile
            app.register_blueprint(profile.bp, url_prefix='/api/profile')
            print("✅ Profile routes registered")
        except ImportError:
            print("⚠️  Profile routes not found (optional)")
        
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
    @app.route('/api/health', methods=['GET', 'OPTIONS'])
    def health():
        if request.method == 'OPTIONS':
            return '', 200
            
        db_status = "disconnected"
        if db.pool:
            try:
                result = db.execute_query("SELECT 1 FROM DUAL", fetch_one=True)
                db_status = "connected" if result else "disconnected"
            except Exception:
                db_status = "error"
        
        return jsonify({
            'status': 'ok',
            'message': 'DineWise API is running',
            'database': db_status,
            'version': '1.0.0'
        }), 200
    
    # Root endpoint
    @app.route('/')
    def root():
        return jsonify({
            'message': 'Welcome to DineWise API',
            'version': '1.0.0'
        }), 200
    
    # Global OPTIONS handler
    @app.before_request
    def handle_preflight():
        from flask import request
        if request.method == 'OPTIONS':
            response = app.make_default_options_response()
            response.headers['Access-Control-Allow-Origin'] = 'http://localhost:5173'
            response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
            response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
            response.headers['Access-Control-Allow-Credentials'] = 'true'
            return response
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({'error': 'Not Found'}), 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({'error': 'Internal Server Error'}), 500
    
    return app
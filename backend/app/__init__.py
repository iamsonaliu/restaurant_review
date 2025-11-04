from flask import Flask
from flask_cors import CORS
from app.config import Config
from app.database import db

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Enable CORS
    CORS(app, origins=app.config['CORS_ORIGINS'])
    
    # Connect to database
    db.connect()
    
    # Register blueprints
    from app.routes import auth, restaurants, reviews, ratings, analytics
    
    app.register_blueprint(auth.bp, url_prefix='/api/auth')
    app.register_blueprint(restaurants.bp, url_prefix='/api/restaurants')
    app.register_blueprint(reviews.bp, url_prefix='/api/reviews')
    app.register_blueprint(ratings.bp, url_prefix='/api/ratings')
    app.register_blueprint(analytics.bp, url_prefix='/api/analytics')
    
    # Health check
    @app.route('/api/health')
    def health():
        return {'status': 'ok', 'message': 'DineWise API is running'}
    
    return app
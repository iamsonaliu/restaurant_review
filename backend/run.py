# backend/run.py
from app import create_app
import os

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'
    
    print(f"""
    ╔══════════════════════════════════════════╗
    ║     🍽️  DineWise Backend API Server     ║
    ╚══════════════════════════════════════════╝
    
    🚀 Server starting...
    📡 API running on: http://localhost:{port}
    🔗 Health check: http://localhost:{port}/api/health
    🌍 Environment: {'Development' if debug else 'Production'}
    📝 API Docs: See backend/README.md
    
    Press CTRL+C to stop the server
    """)
    
    app.run(
        host='0.0.0.0',
        port=port,
        debug=debug
    )
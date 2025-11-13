# backend/run.py
from dotenv import load_dotenv
import os

# Load .env early (before importing app modules that read env vars)
BASE_DIR = os.path.dirname(__file__)
load_dotenv(dotenv_path=os.path.join(BASE_DIR, '.env'))

# Now safe to import app modules
from app import create_app
from app.database import db   # <--- import the instance, not the class

app = create_app()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_ENV') == 'development'

    # Attempt to connect DB and log result
    try:
        connected = db.connect()
        print("Database connected on startup:", connected)
    except Exception as e:
        print("Error while connecting database on startup:", repr(e))

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

    app.run(host='0.0.0.0', port=port, debug=debug)

from flask import Flask
from .database import init_db, db
from flask_migrate import Migrate
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import os
from dotenv import load_dotenv

def create_app():
    """Application factory function"""
    # Load environment variables from .env file
    load_dotenv()

    # Create the Flask application instance
    app = Flask(__name__)

    # Configure the application
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize the database with the app context
    init_db(app)
    
    # Initialize Flask-Migrate
    migrate = Migrate(app, db)

    # Initialize rate limiter
    limiter = Limiter(
        key_func=get_remote_address,
        default_limits=["200 per day", "50 per hour"],
        storage_uri="memory://"
    )
    limiter.init_app(app)

    # Import and register routes
    from . import routes
    routes.init_app(app, limiter)

    return app

# Create app instance for imports
app = create_app() 

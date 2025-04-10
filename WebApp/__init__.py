from flask import Flask
from .database import init_db, db
from flask_migrate import Migrate
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

    # Import and register routes
    from . import routes
    routes.init_app(app)

    return app

# Create app instance for imports
app = create_app() 

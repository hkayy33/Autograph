from flask import Flask, request, jsonify, render_template, redirect, url_for
from WebApp.encryption import Encryptor
from WebApp.models import db, Autograph, InviteCode
from WebApp.routes import init_app
from WebApp.config import Config
from flask_login import LoginManager
from dotenv import load_dotenv
import os
import instaloader
import secrets
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()  
encryption_key = os.getenv('ENCRYPTION_KEY')  # Get the encryption key from the .env file
encryptor = Encryptor(encryption_key)  # Pass the key to the Encryptor

# Create the Flask application instance
app = Flask(__name__)

# Configure the application
app.config.from_object(Config)

# Initialize the database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return InviteCode.query.get(int(user_id))

# Initialize routes
init_app(app)

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()  # Create database tables
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
    
    try:
        app.run(host='0.0.0.0', port=5002, debug=True)
    except Exception as e:
        logger.error(f"Error starting the server: {e}")
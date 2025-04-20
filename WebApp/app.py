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

@app.after_request
def add_security_headers(response):
    """Add security headers to all responses."""
    # Prevent browsers from incorrectly detecting non-scripts as scripts
    response.headers['X-Content-Type-Options'] = 'nosniff'
    # Only allow your site to frame itself
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    # XSS protection 
    response.headers['X-XSS-Protection'] = '1; mode=block'
    # All resources should come from the app's origin
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com https://unpkg.com; style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net https://cdnjs.cloudflare.com; img-src 'self' data:; font-src 'self' https://cdnjs.cloudflare.com; connect-src 'self' https://www.instagram.com;"
    # Set secure cookie attributes
    if 'Set-Cookie' in response.headers:
        response.headers['Set-Cookie'] = response.headers['Set-Cookie'] + '; HttpOnly; SameSite=Lax'
    return response

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
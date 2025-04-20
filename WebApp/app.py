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
from logging.handlers import RotatingFileHandler

# Configure logging
def configure_logging(app):
    if not app.debug and not app.testing:
        # Create logs directory if it doesn't exist
        if not os.path.exists('logs'):
            os.mkdir('logs')
            
        # Set up file logging
        file_handler = RotatingFileHandler('logs/autograph.log', maxBytes=10485760, backupCount=10)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Set log level
        app.logger.setLevel(logging.INFO)
        app.logger.info('Autograph application startup')
        
        # Log startup information
        app.logger.info('Logging system initialized')
        app.logger.info(f'Running in {"debug" if app.debug else "production"} mode')
    else:
        # Set up console logging for development
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        console_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(console_handler)
        app.logger.setLevel(logging.DEBUG)
        
    return app

# Load environment variables
load_dotenv()  
encryption_key = os.getenv('ENCRYPTION_KEY')  # Get the encryption key from the .env file
encryptor = Encryptor(encryption_key)  # Pass the key to the Encryptor

# Create the Flask application instance
app = Flask(__name__)

# Configure the application
app.config.from_object(Config)

# Configure application logging
app = configure_logging(app)

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

# Enforce HTTPS in production
if not app.debug:
    @app.before_request
    def enforce_https():
        if request.headers.get('X-Forwarded-Proto') == 'http':
            url = 'https://' + request.headers['Host'] + request.full_path
            app.logger.info(f'Redirecting HTTP request to HTTPS: {url}')
            return redirect(url, code=301)

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

# Global error handlers
@app.errorhandler(404)
def page_not_found(e):
    app.logger.warning(f"404 Error: {str(e)}")
    return render_template('error.html', 
                          code=404, 
                          title="Page Not Found", 
                          message="The requested page could not be found."), 404

@app.errorhandler(403)
def forbidden(e):
    app.logger.warning(f"403 Error: {str(e)}")
    return render_template('error.html', 
                          code=403, 
                          title="Access Denied", 
                          message="You don't have permission to access this resource."), 403

@app.errorhandler(500)
def internal_server_error(e):
    app.logger.error(f"500 Error: {str(e)}")
    return render_template('error.html', 
                          code=500, 
                          title="Internal Server Error", 
                          message="An unexpected error occurred on our server."), 500

@app.errorhandler(Exception)
def handle_exception(e):
    app.logger.error(f"Unhandled exception: {str(e)}")
    return render_template('error.html',
                          code=500,
                          title="Internal Server Error",
                          message="An unexpected error occurred on our server."), 500

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()  # Create database tables
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {e}")
    
    try:
        app.run(host='0.0.0.0', port=5002, debug=True)
    except Exception as e:
        app.logger.error(f"Error starting the server: {e}")
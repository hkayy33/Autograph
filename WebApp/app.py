from flask import Flask, request, jsonify, render_template, redirect, url_for
from WebApp.encryption import Encryptor
from WebApp.models import db, Autograph, InviteCode
from WebApp.routes import init_app
from WebApp.config import Config
from WebApp.security import configure_security
from flask_login import LoginManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
import instaloader
import secrets
import logging
import logging.handlers

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure file logging if not in debug mode
if not os.getenv('FLASK_DEBUG', '0') == '1':
    if not os.path.exists('logs'):
        os.makedirs('logs')
    file_handler = logging.handlers.RotatingFileHandler(
        'logs/autograph.log', maxBytes=10485760, backupCount=5)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.info('Production logging configured')

# Load environment variables
load_dotenv()  
encryption_key = os.getenv('ENCRYPTION_KEY')
encryptor = Encryptor(encryption_key)

# Create the Flask application instance
app = Flask(__name__)

# Configure the application
app.config.from_object(Config)

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)
limiter.init_app(app)
logger.info('Rate limiter initialized')

# Configure security features
configure_security(app)
logger.info('Security features configured')

# Initialize the database
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return InviteCode.query.get(int(user_id))

# Global error handlers
@app.errorhandler(404)
def page_not_found(e):
    logger.warning(f"Page not found: {request.path}")
    return render_template('error.html', 
                         code=404, 
                         title="Page Not Found", 
                         message="The requested page could not be found."), 404

@app.errorhandler(403)
def forbidden(e):
    logger.warning(f"Forbidden access: {request.path}")
    return render_template('error.html', 
                         code=403, 
                         title="Access Denied", 
                         message="You don't have permission to access this resource."), 403

@app.errorhandler(500)
def internal_server_error(e):
    logger.error(f"Internal Server Error: {str(e)}")
    return render_template('error.html', 
                         code=500, 
                         title="Internal Server Error", 
                         message="An unexpected error occurred on our server."), 500

@app.errorhandler(429)
def ratelimit_handler(e):
    logger.warning(f"Rate limit exceeded: {request.path}")
    return render_template('error.html',
                         code=429,
                         title="Too Many Requests",
                         message="You have exceeded the rate limit. Please try again later."), 429

@app.errorhandler(Exception)
def handle_exception(e):
    logger.error(f"Unhandled exception: {str(e)}")
    return render_template('error.html',
                         code=500,
                         title="Internal Server Error",
                         message="An unexpected error occurred on our server."), 500

# Initialize routes with rate limiter
init_app(app, limiter)

if __name__ == '__main__':
    with app.app_context():
        try:
            db.create_all()
            logger.info("Database tables created successfully")
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
    
    try:
        app.run(host='0.0.0.0', port=5002, debug=True)
    except Exception as e:
        logger.error(f"Error starting the server: {e}")
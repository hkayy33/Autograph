from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from WebApp.encryption import Encryptor
from WebApp.models import db, Autograph, InviteCode
from WebApp.routes import init_app
from WebApp.config import Config
from WebApp.security import configure_security
from WebApp.database import init_db
from WebApp.monitoring import setup_monitoring
from flask_login import LoginManager, current_user, logout_user
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from dotenv import load_dotenv
import os
import instaloader
import secrets
import logging
import argparse
from logging.handlers import RotatingFileHandler
from datetime import datetime, timedelta
from flask import flash
from flask_migrate import Migrate

def configure_logging(app):
    """Configure application logging"""
    if not app.debug and not app.testing:
        # Ensure log directory exists
        if not os.path.exists('logs'):
            os.mkdir('logs')
        
        # File Handler - for general logging
        file_handler = RotatingFileHandler(
            'logs/autograph.log', 
            maxBytes=10485760,  # 10MB
            backupCount=10
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)
        
        # Error File Handler - for errors only
        error_file_handler = RotatingFileHandler(
            'logs/errors.log',
            maxBytes=10485760,
            backupCount=10
        )
        error_file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        error_file_handler.setLevel(logging.ERROR)
        app.logger.addHandler(error_file_handler)
        
        # Set overall log level
        app.logger.setLevel(logging.INFO)
        app.logger.info('Autograph application startup')
    
    return app

def create_app():
    """Application factory function"""
    # Load environment variables from .env file
    load_dotenv()

    # Create the Flask application instance
    app = Flask(__name__)

    # Load configuration
    app.config.from_object('config.Config')
    
    # Initialize monitoring
    setup_monitoring(app)
    
    # Ensure the instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)
    
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

    # Configure logging
    configure_logging(app)

    # Initialize Flask-Login
    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    @login_manager.user_loader
    def load_user(user_id):
        return InviteCode.query.get(int(user_id))

    @app.before_request
    def check_session_timeout():
        """Check for session timeout"""
        if current_user.is_authenticated:
            # Get the last activity time from the session
            last_activity = session.get('last_activity')
            now = datetime.utcnow()
            
            # Set session timeout to 7 days
            session_timeout = timedelta(days=7)
            
            if last_activity:
                last_activity = datetime.fromisoformat(last_activity)
                # If last activity is older than timeout, log out user
                if now - last_activity > session_timeout:
                    app.logger.warning(f'Session expired for user {current_user.instagram_handle}')
                    logout_user()
                    flash('Your session has expired. Please log in again.', 'warning')
                    return redirect(url_for('login'))
            
            # Update last activity time
            session['last_activity'] = now.isoformat()

    # Error handlers
    @app.errorhandler(404)
    def page_not_found(e):
        app.logger.warning(f"Page not found: {request.path} - IP: {request.remote_addr} - User Agent: {request.user_agent}")
        return render_template('error.html', 
                             code=404, 
                             title="Page Not Found", 
                             message="The requested page could not be found."), 404

    @app.errorhandler(403)
    def forbidden(e):
        app.logger.warning(f"Forbidden access: {request.path} - IP: {request.remote_addr} - User: {current_user.instagram_handle if current_user.is_authenticated else 'Anonymous'}")
        return render_template('error.html', 
                             code=403, 
                             title="Access Denied", 
                             message="You don't have permission to access this resource."), 403

    @app.errorhandler(500)
    def internal_server_error(e):
        app.logger.error(f"Internal Server Error: {str(e)} - Path: {request.path} - IP: {request.remote_addr}", exc_info=True)
        return render_template('error.html', 
                             code=500, 
                             title="Internal Server Error", 
                             message="An unexpected error occurred on our server."), 500

    @app.errorhandler(429)
    def ratelimit_handler(e):
        app.logger.warning(f"Rate limit exceeded: {request.path} - IP: {request.remote_addr} - User: {current_user.instagram_handle if current_user.is_authenticated else 'Anonymous'}")
        return render_template('error.html',
                             code=429,
                             title="Too Many Requests",
                             message="You have exceeded the rate limit. Please try again later."), 429

    @app.errorhandler(Exception)
    def handle_exception(e):
        # Log the error with traceback and request details
        app.logger.error(
            f"Unhandled exception: {str(e)}\n"
            f"Path: {request.path}\n"
            f"Method: {request.method}\n"
            f"IP: {request.remote_addr}\n"
            f"User Agent: {request.user_agent}\n"
            f"User: {current_user.instagram_handle if current_user.is_authenticated else 'Anonymous'}",
            exc_info=True
        )
        
        # In production, show generic error message
        if not app.debug:
            return render_template('error.html',
                                code=500,
                                title="Internal Server Error",
                                message="An unexpected error occurred. Our team has been notified."), 500
        
        # In development, show detailed error
        return render_template('error.html',
                            code=500,
                            title="Internal Server Error",
                            message=str(e)), 500

    # Import and register routes
    import WebApp.routes as routes
    routes.init_app(app, limiter)

    return app

# Create the application instance
app = create_app()

if __name__ == '__main__':
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='Run the Autograph Flask application')
    parser.add_argument('--port', type=int, default=5001, help='Port to run the application on')
    args = parser.parse_args()
    
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Error creating database tables: {str(e)}", exc_info=True)
    
    ssl_context = None
    if app.config.get('SSL_ENABLED', False):
        ssl_context = (
            app.config.get('SSL_CERT_PATH'),
            app.config.get('SSL_KEY_PATH')
        )
        app.logger.info(f"SSL enabled with cert: {ssl_context[0]} and key: {ssl_context[1]}")
    
    # Use the port from command line arguments
    app.run(
        host='0.0.0.0',
        port=args.port,
        ssl_context=ssl_context,
        debug=app.config['DEBUG']
    )
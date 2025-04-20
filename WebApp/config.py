import os
from dotenv import load_dotenv
from flask import current_app

# Load environment variables
load_dotenv()

class Config:
    # Use SSL mode for production database connections
    db_url = os.getenv('DATABASE_URL', 'postgresql://autograph_db:hassan@localhost:5432/autograph_db')
    
    # Check if we're using a local database
    is_local = 'localhost' in db_url or '127.0.0.1' in db_url
    
    # Add SSL parameters for non-local connections in production
    if db_url and not is_local:
        if '?' in db_url:
            SQLALCHEMY_DATABASE_URI = f"{db_url}&sslmode=require"
        else:
            SQLALCHEMY_DATABASE_URI = f"{db_url}?sslmode=require"
    else:
        SQLALCHEMY_DATABASE_URI = db_url
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for Flask session management
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set. Please set it in your .env file.")

    # SSL/TLS Configuration
    SSL_ENABLED = os.environ.get('SSL_ENABLED', 'True').lower() == 'true'
    SSL_CERT_PATH = os.environ.get('SSL_CERT_PATH', '/etc/letsencrypt/live/your-domain/fullchain.pem')
    SSL_KEY_PATH = os.environ.get('SSL_KEY_PATH', '/etc/letsencrypt/live/your-domain/privkey.pem')
    
    # Session security
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    PERMANENT_SESSION_LIFETIME = 604800  # 7 days in seconds
    
    # Security headers are configured in security.py
    
    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True
    SSL_ENABLED = False

class ProductionConfig(Config):
    DEBUG = False
    SSL_ENABLED = True
    
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)
        
        # Production-specific configuration
        app.config['PREFERRED_URL_SCHEME'] = 'https'

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

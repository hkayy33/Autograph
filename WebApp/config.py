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

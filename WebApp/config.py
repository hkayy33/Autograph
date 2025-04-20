import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://autograph_db:hassan@localhost:5432/autograph_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Secret key for Flask session management
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set")
    
    # Instagram credentials
    INSTAGRAM_USERNAME = os.getenv('INSTAGRAM_USERNAME')
    INSTAGRAM_PASSWORD = os.getenv('INSTAGRAM_PASSWORD')
    if not INSTAGRAM_USERNAME or not INSTAGRAM_PASSWORD:
        raise ValueError("Instagram credentials are not set in environment variables")

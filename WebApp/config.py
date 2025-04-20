import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'postgresql://autograph_db:hassan@localhost:5432/autograph_db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Get SECRET_KEY from environment variables
    SECRET_KEY = os.getenv('SECRET_KEY')
    if not SECRET_KEY:
        raise ValueError("SECRET_KEY environment variable is not set. Please set it in your .env file.")

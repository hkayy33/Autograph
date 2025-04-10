from flask import Flask
from .database import init_db
import os
from dotenv import load_dotenv

def create_app():
    load_dotenv()
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    init_db(app)
    return app 

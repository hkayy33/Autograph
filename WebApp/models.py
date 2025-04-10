from datetime import datetime
from .database import db

class Autograph(db.Model):
    __tablename__ = 'autographs'
    
    id = db.Column(db.Integer, primary_key=True)
    instagram_url = db.Column(db.String(500), unique=True, nullable=False)
    encrypted_code = db.Column(db.Text, nullable=False)
    raw_code = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Autograph {self.instagram_url[:30]}...>'
    
    

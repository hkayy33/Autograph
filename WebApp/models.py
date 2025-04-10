from datetime import datetime, UTC
from .database import db

class Autograph(db.Model):
    __tablename__ = 'autographs'
    
    id = db.Column(db.Integer, primary_key=True)
    instagram_url = db.Column(db.String(500), unique=True, nullable=False)
    encrypted_code = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(UTC))

    def __repr__(self):
        return f'<Autograph {self.instagram_url[:30]}...>'
    
    

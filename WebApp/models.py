from datetime import datetime
from WebApp.database import db
from flask_login import UserMixin

class Autograph(db.Model):
    __tablename__ = 'autographs'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    instagram_url = db.Column(db.String(255), nullable=False)
    encryption_code = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Autograph {self.instagram_url[:30]}...>'

class InviteCode(db.Model, UserMixin):
    __tablename__ = 'invite_codes'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(32), nullable=False, unique=True)
    instagram_handle = db.Column(db.String(80), nullable=False)
    is_used = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    used_at = db.Column(db.DateTime, nullable=True)

    def get_id(self):
        return str(self.id)

    @staticmethod
    def authenticate(instagram_handle, code):
        user = InviteCode.query.filter_by(
            instagram_handle=instagram_handle.lower().strip(),
            code=code.strip()
        ).first()
        if user:
            # Update usage tracking but allow reuse
            if not user.is_used:
                user.is_used = True
                user.used_at = datetime.utcnow()
                db.session.commit()
            return user
        return None

    @property
    def is_admin(self):
        return self.instagram_handle.lower() == 'admin'
    
    

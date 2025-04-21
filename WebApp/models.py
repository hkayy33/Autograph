from datetime import datetime
from WebApp.database import db, safe_query, safe_first, safe_all
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

    @classmethod
    def find_by_instagram_url(cls, url):
        """Safely find an autograph by Instagram URL"""
        return safe_first(
            "SELECT * FROM autographs WHERE instagram_url LIKE :url",
            {"url": f"%{url}%"}
        )

    @classmethod
    def find_by_encryption_code(cls, code):
        """Safely find an autograph by encryption code"""
        return safe_first(
            "SELECT * FROM autographs WHERE encryption_code = :code",
            {"code": code}
        )

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

    @property
    def is_active(self):
        """Required by Flask-Login, determines if this is an active user"""
        return True  # All invite codes are considered active users

    @property
    def is_admin(self):
        return self.instagram_handle.lower() == 'admin'

    @staticmethod
    def authenticate(instagram_handle, code):
        """Safely authenticate a user with their Instagram handle and code"""
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

    @classmethod
    def find_by_handle(cls, handle):
        """Safely find a user by Instagram handle"""
        return cls.query.filter_by(
            instagram_handle=handle.lower().strip()
        ).first()

    @classmethod
    def get_all_codes(cls):
        """Safely get all invite codes"""
        return cls.query.order_by(cls.created_at.desc()).all()
    
    

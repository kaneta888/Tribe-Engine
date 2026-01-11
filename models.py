from datetime import datetime
from flask_login import UserMixin
from extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    
    # Roles: 'free', 'paid', 'admin', 'owner'
    role = db.Column(db.String(20), default='free', nullable=False)
    
    # SMS & Profile
    phone_number = db.Column(db.String(20), nullable=True)
    avatar_path = db.Column(db.String(200), nullable=True)  # Profile icon path
    sms_opt_in = db.Column(db.Boolean, default=False)
    
    # Admin/Owner specific
    sms_credits = db.Column(db.Integer, default=0)  # Prepaid credits
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Password reset
    reset_token = db.Column(db.String(100), nullable=True)
    reset_token_expiry = db.Column(db.DateTime, nullable=True)

    def is_paid_user(self):
        return self.role in ['paid', 'admin', 'owner']

    def is_admin(self):
        return self.role in ['admin', 'owner']
    
    def is_owner(self):
        return self.role == 'owner'

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    image_path = db.Column(db.String(255), nullable=True)
    
    # Post type: 'normal', 'announcement'
    post_type = db.Column(db.String(20), default='normal')
    
    # Visibility: 'all', 'paid', 'admin'
    visibility = db.Column(db.String(20), default='all')
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    author = db.relationship('User', backref=db.backref('posts', lazy=True))
    comments = db.relationship('Comment', backref='post', lazy=True, cascade="all, delete-orphan")
    likes = db.relationship('Like', backref='post', lazy=True, cascade="all, delete-orphan")

    @property
    def like_count(self):
        return len(self.likes)

    def is_liked_by(self, user):
        return Like.query.filter_by(user_id=user.id, post_id=self.id).first() is not None

    def is_saved_by(self, user):
        return SavedPost.query.filter_by(user_id=user.id, post_id=self.id).first() is not None

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    author = db.relationship('User', backref=db.backref('comments', lazy=True))

class SMSLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    target_count = db.Column(db.Integer, nullable=False)
    cost = db.Column(db.Integer, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    sender = db.relationship('User', backref=db.backref('sms_logs', lazy=True))

class Like(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Unique constraint to prevent double likes
    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='_user_post_uc'),)

class SavedPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    post_id = db.Column(db.Integer, db.ForeignKey('post.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('user_id', 'post_id', name='_user_post_saved_uc'),)

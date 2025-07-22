from app import db
from flask_login import UserMixin
from datetime import datetime, timedelta
from sqlalchemy import func

class User(UserMixin, db.Model):
    """
    User model representing registered users in the Alpha Nex platform.
    Includes XP tracking, strike system, and activity monitoring.
    """
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_verified = db.Column(db.Boolean, default=False)
    xp_points = db.Column(db.Integer, default=0)
    uploader_strikes = db.Column(db.Integer, default=0)
    reviewer_strikes = db.Column(db.Integer, default=0)
    is_banned = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # User verification (simplified - no KYC required)
    is_active = db.Column(db.Boolean, default=True)
    
    # Daily upload tracking
    daily_upload_bytes = db.Column(db.Integer, default=0)
    daily_upload_reset = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    uploads = db.relationship('Upload', backref='user', lazy=True)
    reviews = db.relationship('Review', backref='reviewer', lazy=True)
    strikes = db.relationship('Strike', backref='user', lazy=True)
    withdrawals = db.relationship('WithdrawalRequest', backref='user', lazy=True)
    
    def get_daily_upload_remaining(self):
        """Calculate remaining daily upload capacity in bytes"""
        # Reset daily counter if it's a new day
        if datetime.utcnow().date() > self.daily_upload_reset.date():
            self.daily_upload_bytes = 0
            self.daily_upload_reset = datetime.utcnow()
            db.session.commit()
        
        max_daily = 500 * 1024 * 1024  # 500MB in bytes
        return max_daily - self.daily_upload_bytes
    
    def can_upload(self, file_size):
        return self.get_daily_upload_remaining() >= file_size and not self.is_banned
    
    def add_strike(self, strike_type, reason):
        strike = Strike(user_id=self.id, strike_type=strike_type, reason=reason)
        db.session.add(strike)
        
        if strike_type == 'uploader':
            self.uploader_strikes += 1
        elif strike_type == 'reviewer':
            self.reviewer_strikes += 1
            
        # Ban user if they reach 3 strikes in either category
        if self.uploader_strikes >= 3 or self.reviewer_strikes >= 3:
            self.is_banned = True
            
        db.session.commit()

class Upload(db.Model):
    """
    Upload model for storing file submissions and metadata.
    Tracks file information, AI analysis results, and review status.
    """
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    ai_consent = db.Column(db.Boolean, default=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    deletion_deadline = db.Column(db.DateTime)
    
    # AI analysis results
    duplicate_score = db.Column(db.Float, default=0.0)
    spam_score = db.Column(db.Float, default=0.0)
    
    # Review tracking
    reviews = db.relationship('Review', backref='upload', lazy=True, cascade='all, delete-orphan')
    
    def __init__(self, **kwargs):
        super(Upload, self).__init__(**kwargs)
        # Set deletion deadline to 48 hours from upload
        self.deletion_deadline = datetime.utcnow() + timedelta(hours=48)
    
    def get_average_rating(self):
        if not self.reviews:
            return None
        good_reviews = sum(1 for r in self.reviews if r.rating == 'good')
        return good_reviews / len(self.reviews)
    
    def can_delete_free(self):
        return datetime.utcnow() < self.deletion_deadline
    
    def get_deletion_penalty(self):
        if self.can_delete_free():
            return 0
        # Penalty increases based on how long after deadline
        hours_late = (datetime.utcnow() - self.deletion_deadline).total_seconds() / 3600
        return min(int(hours_late * 5), 100)  # Max 100 XP penalty

class Review(db.Model):
    """
    Review model for storing user feedback and ratings.
    Now used for website feedback instead of content reviews.
    """
    id = db.Column(db.Integer, primary_key=True)
    upload_id = db.Column(db.Integer, db.ForeignKey('upload.id'), nullable=False)
    reviewer_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.String(10), nullable=False)  # 'good' or 'bad'
    description = db.Column(db.Text, nullable=False)
    xp_earned = db.Column(db.Integer, default=10)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Quality tracking for reviewer strikes
    is_flagged = db.Column(db.Boolean, default=False)
    quality_score = db.Column(db.Float, default=1.0)

class Strike(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    strike_type = db.Column(db.String(20), nullable=False)  # 'uploader' or 'reviewer'
    reason = db.Column(db.String(500), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class WithdrawalRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    amount_xp = db.Column(db.Integer, nullable=False)
    amount_usd = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    payment_method = db.Column(db.String(100))
    payment_details = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    processed_at = db.Column(db.DateTime)
    admin_notes = db.Column(db.Text)

class AdminAction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    admin_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    action_type = db.Column(db.String(50), nullable=False)
    target_id = db.Column(db.Integer, nullable=False)  # ID of affected user/upload/etc
    description = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

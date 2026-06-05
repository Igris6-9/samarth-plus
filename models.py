from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

# 🏗️ DAKASH ENGINE - NEURAL DATABASE INITIALIZATION
db = SQLAlchemy()

# 👤 USER TABLE: The Command Center Identity
class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Adaptive Ranking: Cadet ki progress ke hisab se change hoga
    rank = db.Column(db.String(30), default="RECRUIT ⚔️")
    avatar = db.Column(db.String(100), default="default_avatar.png") # Future update ke liye
    
    # Neural Timestamps (PC Standard)
    date_joined = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships: Direct Neural Links
    scores = db.relationship('Score', backref='cadet', lazy='dynamic', cascade="all, delete-orphan")
    goals = db.relationship('Goal', backref='cadet', lazy='dynamic', cascade="all, delete-orphan")
    timetable = db.relationship('Timetable', backref='cadet', lazy='dynamic', cascade="all, delete-orphan")

    # FIX: Password hashing logic for secure storage
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

# 📊 SCORE TABLE: Mission Performance Data
class Score(db.Model):
    __tablename__ = 'score'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    subject_name = db.Column(db.String(50), nullable=False)
    score_val = db.Column(db.Integer, nullable=False)
    total_val = db.Column(db.Integer, nullable=False)
    test_type = db.Column(db.String(20)) # 'QUIZ', 'PRACTICE', 'BOARD_MOCK'
    date_recorded = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# 🎯 GOAL TABLE: Strategic Trajectories
class Goal(db.Model):
    __tablename__ = 'goal'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), default="Side Quest") 
    status = db.Column(db.String(20), default="ACTIVE") # ACTIVE, ACCOMPLISHED, FAILED
    deadline = db.Column(db.String(50))
    date_created = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

# 📅 TIMETABLE TABLE: The Daily Combat Plan
class Timetable(db.Model):
    __tablename__ = 'timetable'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    time_slot = db.Column(db.String(30), nullable=False)
    task_name = db.Column(db.String(100), nullable=False)
    details = db.Column(db.String(255))
    priority = db.Column(db.String(20), default="Medium") # Low, Medium, High
    is_completed = db.Column(db.Boolean, default=False)
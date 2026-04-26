from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
import random

db = SQLAlchemy()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    phone = db.Column(db.String(20), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)

    wishes = db.relationship('Wish', backref='owner', lazy='dynamic', cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='voter', lazy='dynamic')
    achievements = db.relationship('Achievement', backref='user', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def update_activity(self):
        self.last_active = datetime.utcnow()
        db.session.commit()

    def get_active_wishes(self):
        return Wish.query.filter_by(user_id=self.id, is_completed=False).all()

    def get_public_wishes(self):
        return Wish.query.filter_by(user_id=self.id, is_public=True, is_completed=False).all()

    def __repr__(self):
        return f'<User {self.name} ({self.phone})>'


class Wish(db.Model):
    __tablename__ = 'wishes'

    WISH_TYPES = [
        ('money', 'Накопить деньги'),
        ('progress', 'Прогресс (км, страницы, часы)')
    ]

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)

    wish_type = db.Column(db.String(20), default='money')
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0)
    unit_label = db.Column(db.String(50), default='руб.')

    deadline = db.Column(db.DateTime, nullable=True)
    daily_target = db.Column(db.Float, nullable=True)

    growth_percent = db.Column(db.Integer, default=0)
    last_contribution = db.Column(db.DateTime, default=datetime.utcnow)
    wilting_days = db.Column(db.Integer, default=0)
    flower_stage = db.Column(db.String(20), default='seed')

    is_public = db.Column(db.Boolean, default=False)
    is_completed = db.Column(db.Boolean, default=False)
    is_magic_slot_enabled = db.Column(db.Boolean, default=True)
    icon_path = db.Column(db.String(300), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)

    contributions = db.relationship('Contribution', backref='wish', lazy='dynamic', cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='wish', lazy='dynamic')

    def calculate_growth(self):
        if self.target_amount > 0:
            self.growth_percent = min(100, int((self.current_amount / self.target_amount) * 100))
        else:
            self.growth_percent = 0
        self.update_flower_stage()
        return self.growth_percent

    def update_flower_stage(self):
        days_no_add = (datetime.utcnow() - self.last_contribution).days
        self.wilting_days = max(0, days_no_add - 2)

        if self.is_completed:
            self.flower_stage = 'bloom'
        elif self.wilting_days > 3:
            self.flower_stage = 'wilted'
        elif self.growth_percent == 0:
            self.flower_stage = 'seed'
        elif self.growth_percent < 30:
            self.flower_stage = 'sprout'
        elif self.growth_percent < 60:
            self.flower_stage = 'growing'
        elif self.growth_percent < 100:
            self.flower_stage = 'bud'
        else:
            self.flower_stage = 'flower'

    def add_contribution(self, amount, note=None, is_magic=False):
        self.current_amount += amount
        self.last_contribution = datetime.utcnow()
        self.wilting_days = 0

        contrib = Contribution(wish_id=self.id, amount=amount, note=note, is_magic=is_magic)
        db.session.add(contrib)

        self.calculate_growth()

        if self.current_amount >= self.target_amount:
            self.complete_wish()

        db.session.commit()
        return contrib

    def complete_wish(self):
        self.is_completed = True
        self.completed_at = datetime.utcnow()
        self.growth_percent = 100
        self.flower_stage = 'bloom'

        # перенос в достижения
        achievement = Achievement(
            user_id=self.user_id,
            wish_id=self.id,
            title=f'Исполнено: {self.title}',
            description=self.description,
            icon_path=self.icon_path,
            total_amount=self.current_amount
        )
        db.session.add(achievement)
        db.session.commit()

    def calculate_daily_target(self):
        if self.deadline and not self.is_completed:
            days_left = (self.deadline - datetime.utcnow()).days
            if days_left > 0:
                remaining = self.target_amount - self.current_amount
                self.daily_target = remaining / days_left
            else:
                self.daily_target = 0
        return self.daily_target

    def get_vote_count(self):
        return Vote.query.filter_by(wish_id=self.id).count()

    def __repr__(self):
        return f'<Wish {self.title} ({self.growth_percent}%)>'


class Contribution(db.Model):
    __tablename__ = 'contributions'

    id = db.Column(db.Integer, primary_key=True)
    wish_id = db.Column(db.Integer, db.ForeignKey('wishes.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    note = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_magic = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<Contribution {self.amount} to wish {self.wish_id}>'


class Vote(db.Model):
    __tablename__ = 'votes'

    id = db.Column(db.Integer, primary_key=True)
    wish_id = db.Column(db.Integer, db.ForeignKey('wishes.id'), nullable=False)
    voter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (db.UniqueConstraint('wish_id', 'voter_id', name='unique_vote'),)

    def __repr__(self):
        return f'<Vote for wish {self.wish_id} by user {self.voter_id}>'


class Achievement(db.Model):
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    wish_id = db.Column(db.Integer, db.ForeignKey('wishes.id'), nullable=True)

    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    icon_path = db.Column(db.String(300))
    total_amount = db.Column(db.Float)
    completed_at = db.Column(db.DateTime, default=datetime.utcnow)

    achievement_photo = db.Column(db.String(300))

    def __repr__(self):
        return f'<Achievement {self.title}>'


class MagicSlotSession(db.Model):
    __tablename__ = 'magic_slot_sessions'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    amount = db.Column(db.Float, nullable=False)
    target_wish_id = db.Column(db.Integer, db.ForeignKey('wishes.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<MagicSlot {self.amount} -> Wish {self.target_wish_id}>'

from datetime import datetime
from flask_login import UserMixin

from extensions import db


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    memberships = db.relationship('Membership', back_populates='user', lazy='dynamic')
    created_groups = db.relationship('Group', back_populates='creator', lazy='dynamic')

    def __repr__(self):
        return f'<User {self.email}>'


class Group(db.Model):
    __tablename__ = 'groups'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='AUD')
    invite_code = db.Column(db.String(10), unique=True, nullable=False, index=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    creator = db.relationship('User', back_populates='created_groups')
    memberships = db.relationship('Membership', back_populates='group', lazy='dynamic')
    expenses = db.relationship('Expense', back_populates='group', lazy='dynamic')

    def __repr__(self):
        return f'<Group {self.name}>'


class Membership(db.Model):
    __tablename__ = 'memberships'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='member')
    joined_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user = db.relationship('User', back_populates='memberships')
    group = db.relationship('Group', back_populates='memberships')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'group_id', name='unique_user_group'),
    )

    def __repr__(self):
        return f'<Membership user_id={self.user_id} group_id={self.group_id} role={self.role}>'


class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.Integer, db.ForeignKey('groups.id'), nullable=False)
    paid_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False, default=datetime.utcnow().date)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    group = db.relationship('Group', back_populates='expenses')
    payer = db.relationship('User', foreign_keys=[paid_by])

    def __repr__(self):
        return f'<Expense {self.description} ${self.amount}>'
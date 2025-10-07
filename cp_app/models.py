from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from . import db


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False, unique=True)
    text = db.Column(db.Text, unique=True, nullable=False)

    def to_dict(self):
        return dict(
            id=self.id,
            title=self.title,
            text=self.text,
        )

    def from_dict(self, data):
        for field in ['title', 'text']:
            if field in data:
                setattr(self, field, data[field])


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_admin = db.Column(db.Boolean, default=False)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    question_id = db.Column(
        db.Integer, db.ForeignKey('question.id'), nullable=False
    )

    user = db.relationship('User', backref='comments')
    question = db.relationship('Question', backref='comments')

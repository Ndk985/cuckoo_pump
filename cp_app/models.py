from . import db


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False, unique=True)
    text = db.Column(db.Text, unique=True, nullable=False)

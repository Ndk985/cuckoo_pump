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

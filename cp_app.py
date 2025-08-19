from datetime import datetime
from random import randrange

from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

db = SQLAlchemy(app)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    text = db.Column(db.Text, unique=True, nullable=False)


@app.route('/')
def index_view():
    quantity = Question.query.count()
    if not quantity:
        return 'В базе данных нет вопросов.'
    offset_value = randrange(quantity)
    question = Question.query.offset(offset_value).first()
    return render_template('question.html', question=question)


@app.route('/add')
def add_question_view():
    return render_template('add_question.html')


if __name__ == '__main__':
    app.run()

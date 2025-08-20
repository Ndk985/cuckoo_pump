from datetime import datetime
from random import randrange

from flask import Flask, abort, flash, redirect, render_template, url_for
from flask_sqlalchemy import SQLAlchemy

from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import DataRequired, Length, Optional


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SECRET_KEY'] = 'MAY THE FORCE BE WITH YOU'

db = SQLAlchemy(app)


class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    text = db.Column(db.Text, unique=True, nullable=False)


class OpinionForm(FlaskForm):
    title = StringField(
        'Введите вопрос',
        validators=[DataRequired(message='Обязательное поле'),
                    Length(1, 128)]
    )
    text = TextAreaField(
        'Напишите ответ',
        validators=[DataRequired(message='Обязательное поле')]
    )
    submit = SubmitField('Добавить')


@app.route('/')
def index_view():
    quantity = Question.query.count()
    if not quantity:
        abort(500)
    offset_value = randrange(quantity)
    question = Question.query.offset(offset_value).first()
    return render_template('question.html', question=question)


@app.route('/add')
def add_question_view():
    return render_template('add_question.html')


@app.route('/questions/<int:id>')
def question_view(id):
    question = Question.query.get_or_404(id)
    return render_template('question.html', question=question)


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500


@app.errorhandler(404)
def page_not_found(error):
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run()

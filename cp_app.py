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
    title = db.Column(db.String(128), nullable=False, unique=True)
    text = db.Column(db.Text, unique=True, nullable=False)


class QuestionForm(FlaskForm):
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


@app.route('/add', methods=['GET', 'POST'])
def add_question_view():
    form = QuestionForm()
    if form.validate_on_submit():
        title = form.title.data
        if Question.query.filter_by(title=title).first() is not None:
            flash('Такой вопрос уже был записан ранее!')
            return render_template('add_question.html', form=form)
        question = Question(
            title=title,
            text=form.text.data,
        )
        db.session.add(question)
        db.session.commit()
        return redirect(url_for('question_view', id=question.id))
    return render_template('add_question.html', form=form)


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

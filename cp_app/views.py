from random import randrange

from flask import abort, flash, redirect, render_template, url_for

from . import app, db
from .forms import QuestionForm
from .models import Question


def random_question():
    quantity = Question.query.count()
    if quantity:
        offset_value = randrange(quantity)
        opinion = Question.query.offset(offset_value).first()
        return opinion


@app.route('/')
def index_view():
    question = random_question()
    if question is None:
        abort(500)
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

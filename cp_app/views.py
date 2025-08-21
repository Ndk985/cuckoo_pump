from random import randrange

from flask import abort, flash, redirect, render_template, url_for

from . import app, db
from .forms import QuestionForm
from .models import Question


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

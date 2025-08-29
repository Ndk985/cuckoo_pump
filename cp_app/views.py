from random import randrange
from functools import wraps

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user, login_required, current_user

from . import app, db
from .forms import LoginForm, QuestionForm, RegistrationForm
from .models import Question, User


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin:
            abort(403)
        return f(*args, **kwargs)
    return decorated


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
@admin_required
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


@app.route('/questions/<int:id>/edit', methods=['GET', 'POST'])
@admin_required
def edit_question_view(id):
    question = Question.query.get_or_404(id)

    form = QuestionForm(obj=question)
    if form.validate_on_submit():
        form.populate_obj(question)
        db.session.commit()
        flash('Вопрос обновлён')
        return redirect(url_for('question_view', id=question.id))

    return render_template('add_question.html',
                           form=form,
                           edit_mode=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index_view'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            return redirect(request.args.get('next') or url_for('index_view'))
        flash('Неверный логин или пароль')
    return render_template('login.html', form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли из системы')
    return redirect(url_for('index_view'))


@app.route('/register', methods=['GET', 'POST'])
# @login_required
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash('Такой пользователь уже существует')
            return redirect(url_for('register'))
        user = User(username=form.username.data, is_admin=False)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Пользователь создан')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

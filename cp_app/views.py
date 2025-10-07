from random import randrange
from functools import wraps

from flask import abort, flash, redirect, render_template, request, url_for
from flask_login import login_user, logout_user, login_required, current_user

from . import app, db
from .forms import LoginForm, QuestionForm, RegistrationForm, CommentForm
from .models import Question, User, Comment
from .quiz import *   # noqa


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
    return redirect(url_for('main_page'))


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


@app.route('/questions/<int:id>', methods=['GET', 'POST'])
def question_view(id):
    question = Question.query.get_or_404(id)
    form = CommentForm()

    if form.validate_on_submit():
        if not current_user.is_authenticated:
            flash('Войдите, чтобы оставить комментарий')
            return redirect(url_for('login'))

        comment = Comment(
            text=form.text.data,
            user_id=current_user.id,
            question_id=question.id
        )
        db.session.add(comment)
        db.session.commit()
        flash('Комментарий добавлен')
        return redirect(url_for('question_view', id=id))

    comments = Comment.query.filter_by(question_id=id).order_by(
        Comment.timestamp.desc()
    ).all()
    return render_template(
        'question.html', question=question, form=form, comments=comments
    )


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


@app.route('/main')
def main_page():
    return render_template('main.html')


@app.route('/random-question')
def random_question_page():
    question = random_question()
    if question is None:
        abort(500)

    from .forms import CommentForm
    form = CommentForm()
    comments = Comment.query.filter_by(question_id=question.id)\
                            .order_by(Comment.timestamp.desc()).all()
    return render_template(
        'question.html',
        question=question,
        form=form,
        comments=comments
    )


@app.route('/questions')
def all_questions():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    pagination = Question.query.order_by(Question.id).paginate(
        page=page, per_page=per_page
    )
    questions = pagination.items
    return render_template(
        'questions_list.html', questions=questions, pagination=pagination
    )

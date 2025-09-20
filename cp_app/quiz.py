from random import sample

from flask import (
     Blueprint, redirect, render_template, request, url_for, session
)

from cp_app.models import Question

quiz_bp = Blueprint('quiz', __name__, url_prefix='/quiz')


@quiz_bp.route('/start', methods=['GET'])
def quiz_start():
    """Заглушка: пока просто рендерим шаблон с кнопкой «Начать»."""
    return render_template('quiz_start.html')


@quiz_bp.route('/begin', methods=['POST'])
def quiz_begin():
    """Создаёт список из 10 id-вопросов и кладёт его в session."""
    all_ids = [q.id for q in Question.query.all()]
    if len(all_ids) < 10:
        # если вопросов мало, берём сколько есть
        session['quiz_ids'] = sample(all_ids, k=len(all_ids))
        session['quiz_total'] = len(all_ids)
    else:
        session['quiz_ids'] = sample(all_ids, k=10)
        session['quiz_total'] = 10

    session['quiz_index'] = 0
    session['quiz_correct'] = 0
    return redirect(url_for('quiz.quiz_step', n=0))


@quiz_bp.route('/step/<int:n>')
def quiz_step(n):
    # пока убираем строгую проверку
    q_id = session['quiz_ids'][n]  # если n вне диапазона → IndexError, это ОК
    question = Question.query.get_or_404(q_id)
    return render_template('quiz_step.html', question=question, n=n)


@quiz_bp.route('/reveal/<int:n>', methods=['POST'])
def quiz_reveal(n):
    q_id = session['quiz_ids'][n]
    question = Question.query.get_or_404(q_id)
    return render_template('quiz_reveal.html', question=question, n=n)


@quiz_bp.route('/mark/<int:n>', methods=['POST'])
def quiz_mark(n):
    if request.form.get('mark') == 'answered':
        session['quiz_correct'] = session.get('quiz_correct', 0) + 1

    next_n = n + 1
    if next_n >= session['quiz_total']:
        return redirect(url_for('quiz.finish'))

    return redirect(url_for('quiz.quiz_step', n=next_n))


@quiz_bp.route('/finish')
def finish():
    correct = session.get('quiz_correct', 0)
    total = session.get('quiz_total', 10)
    return render_template('quiz_finish.html', correct=correct, total=total)


@quiz_bp.route('/reset', methods=['POST'])
def reset():
    session.pop('quiz_ids', None)
    session.pop('quiz_index', None)
    session.pop('quiz_correct', None)
    session.pop('quiz_total', None)
    return redirect(url_for('quiz.quiz_start'))

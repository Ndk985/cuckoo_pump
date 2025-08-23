from flask import jsonify, request

from . import app, db
from .models import Question
from .views import random_question

from .error_handlers import InvalidAPIUsage


@app.route('/api/questions/<int:id>/', methods=['GET'])
def get_question(id):
    question = Question.query.get(id)
    if question is None:
        raise InvalidAPIUsage('Вопроса с указанным id не найдено', 404)
    return jsonify({'question': question.to_dict()}), 200


@app.route('/api/questions/<int:id>/', methods=['PATCH'])
def update_question(id):
    data = request.get_json()
    question = Question.query.get(id)
    if question is None:
        raise InvalidAPIUsage('Вопрос с указанным id не найден', 404)
    question.title = data.get('title', question.title)
    question.text = data.get('text', question.text)
    db.session.commit()
    return jsonify({'question': question.to_dict()}), 200


@app.route('/api/questions/<int:id>/', methods=['DELETE'])
def delete_question(id):
    question = Question.query.get(id)
    if question is None:
        raise InvalidAPIUsage(' Вопрос с указанным id не найден', 404)
    db.session.delete(question)
    db.session.commit()
    return '', 204


@app.route('/api/questions/', methods=['GET'])
def get_questions():
    questions = Question.query.all()
    questions_list = [question.to_dict() for question in questions]
    return jsonify({'questions': questions_list}), 200


@app.route('/api/questions/', methods=['POST'])
def add_question():
    data = request.get_json()
    if 'title' not in data or 'text' not in data:
        raise InvalidAPIUsage('В запросе отсутствуют обязательные поля')
    if Question.query.filter_by(title=data['title']).first() is not None:
        raise InvalidAPIUsage('Такой вопрос уже есть в базе данных')
    question = Question()
    question.from_dict(data)
    db.session.add(question)
    db.session.commit()
    return jsonify({'question': question.to_dict()}), 201


@app.route('/api/get-random-question/', methods=['GET'])
def get_random_question():
    question = random_question()
    if question is not None:
        return jsonify({'opinion': question.to_dict()}), 200
    raise InvalidAPIUsage('В базе данных нет мнений', 404)

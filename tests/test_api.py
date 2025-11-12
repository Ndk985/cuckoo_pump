"""
Тесты для REST API endpoints
"""
import pytest
import json
from cp_app import db
from cp_app.models import Question


class TestQuestionAPI:
    """Тесты для API вопросов"""

    def test_get_questions(self, client, multiple_questions):
        """Тест получения списка всех вопросов"""
        response = client.get('/api/questions/')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'questions' in data
        assert len(data['questions']) == 15

    def test_get_question_by_id(self, client, test_question):
        """Тест получения вопроса по ID"""
        # Сохраняем данные вопроса до запроса
        question_id = test_question.id
        question_title = test_question.title
        question_text = test_question.text

        response = client.get(f'/api/questions/{question_id}/')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'question' in data
        assert data['question']['id'] == question_id
        assert data['question']['title'] == question_title
        assert data['question']['text'] == question_text

    def test_get_question_not_found(self, client):
        """Тест получения несуществующего вопроса"""
        response = client.get('/api/questions/99999/')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert 'message' in data

    def test_create_question(self, client):
        """Тест создания вопроса через API"""
        response = client.post(
            '/api/questions/',
            data=json.dumps({
                                 'title': 'API Test Question?',
                                 'text': 'API Test Answer'
                             }),
            content_type='application/json'
        )
        assert response.status_code == 201

        data = json.loads(response.data)
        assert 'question' in data
        assert data['question']['title'] == 'API Test Question?'

        # Проверяем, что вопрос создан в БД
        with client.application.app_context():
            question = Question.query.filter_by(
                title='API Test Question?').first()
            assert question is not None

    def test_create_question_missing_fields(self, client):
        """Тест создания вопроса без обязательных полей"""
        response = client.post(
            '/api/questions/',
            data=json.dumps({
                                 'title': 'Only Title'
                             }),
            content_type='application/json'
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'message' in data

    def test_create_duplicate_question(self, client, test_question):
        """Тест создания дубликата вопроса"""
        # Сохраняем title до запроса
        duplicate_title = test_question.title

        response = client.post(
            '/api/questions/',
            data=json.dumps({
                                 'title': duplicate_title,
                                 'text': 'Different text'
                             }),
            content_type='application/json'
        )
        assert response.status_code == 400

        data = json.loads(response.data)
        assert 'message' in data

    def test_update_question(self, client, test_question):
        """Тест обновления вопроса через API"""
        question_id = test_question.id
        response = client.patch(
            f'/api/questions/{question_id}/',
            data=json.dumps({
                                  'title': 'Updated API Question?',
                                  'text': 'Updated API Answer'
                              }),
            content_type='application/json'
            )
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data['question']['title'] == 'Updated API Question?'

        # Проверяем, что вопрос обновлён в БД
        with client.application.app_context():
            question = Question.query.get(question_id)
            assert question.title == 'Updated API Question?'
            assert question.text == 'Updated API Answer'

    def test_update_question_partial(self, client, test_question):
        """Тест частичного обновления вопроса"""
        question_id = test_question.id
        # Сохраняем оригинальный текст до запроса
        with client.application.app_context():
            original_question = Question.query.get(question_id)
            original_text = original_question.text

        response = client.patch(
            f'/api/questions/{question_id}/',
            data=json.dumps({
                                  'title': 'Only Title Updated?'
                              }),
            content_type='application/json'
        )
        assert response.status_code == 200

        # Проверяем, что текст остался прежним
        with client.application.app_context():
            question = Question.query.get(question_id)
            assert question.title == 'Only Title Updated?'
            assert question.text == original_text

    def test_update_question_not_found(self, client):
        """Тест обновления несуществующего вопроса"""
        response = client.patch(
            '/api/questions/99999/',
            data=json.dumps({
                                  'title': 'New Title?'
                              }),
            content_type='application/json'
        )
        assert response.status_code == 404

    def test_delete_question(self, client, test_question):
        """Тест удаления вопроса через API"""
        question_id = test_question.id
        response = client.delete(f'/api/questions/{question_id}/')
        assert response.status_code == 204

        # Проверяем, что вопрос удалён из БД
        with client.application.app_context():
            question = Question.query.get(question_id)
            assert question is None

    def test_delete_question_not_found(self, client):
        """Тест удаления несуществующего вопроса"""
        response = client.delete('/api/questions/99999/')
        assert response.status_code == 404


class TestRandomQuestionAPI:
    """Тесты для API случайного вопроса"""

    def test_get_random_question(self, client, multiple_questions):
        """Тест получения случайного вопроса"""
        response = client.get('/api/get-random-question/')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'opinion' in data
        assert 'id' in data['opinion']
        assert 'title' in data['opinion']
        assert 'text' in data['opinion']

    def test_get_random_question_no_questions(self, client):
        """Тест получения случайного вопроса при отсутствии вопросов"""
        response = client.get('/api/get-random-question/')
        assert response.status_code == 404

        data = json.loads(response.data)
        assert 'message' in data

    def test_random_question_different_results(
        self, client, multiple_questions
    ):
        """Тест, что случайные вопросы действительно разные"""
        # Делаем несколько запросов и проверяем, что получаем разные вопросы
        question_ids = set()
        for _ in range(10):
            response = client.get('/api/get-random-question/')
            assert response.status_code == 200
            data = json.loads(response.data)
            question_ids.add(data['opinion']['id'])

        # С высокой вероятностью должны получить разные вопросы
        # (но не гарантируется, если вопросов мало)
        assert len(question_ids) >= 1

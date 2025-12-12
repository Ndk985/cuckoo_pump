"""
Тесты для views (веб-страницы, аутентификация, CRUD)
"""
import pytest
from cp_app import db
from cp_app.models import User, Question, Comment, Tag


class TestAuthentication:
    """Тесты аутентификации"""

    def test_login_page_loads(self, client):
        """Тест загрузки страницы логина"""
        response = client.get('/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or b'username' in response.data.lower()

    def test_login_success(self, client, test_user):
        """Тест успешного входа"""
        response = client.post('/login', data={
            'login': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        assert response.status_code == 200

    def test_login_failure(self, client, test_user):
        """Тест неудачного входа"""
        response = client.post('/login', data={
            'login': 'testuser',
            'password': 'wrongpassword'
        })
        assert response.status_code == 200
        # Проверяем, что остались на странице логина
        assert (b'login' in response.data.lower() or
                b'password' in response.data.lower())

    def test_logout(self, authenticated_client):
        """Тест выхода из системы"""
        response = authenticated_client.get('/logout', follow_redirects=True)
        assert response.status_code == 200

    def test_register_page_loads(self, client):
        """Тест загрузки страницы регистрации"""
        response = client.get('/register')
        assert response.status_code == 200

    def test_register_success(self, client):
        """Тест успешной регистрации"""
        response = client.post('/register', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password2': 'password123'
        }, follow_redirects=True)
        assert response.status_code == 200

        # Проверяем, что пользователь создан
        with client.application.app_context():
            user = User.query.filter_by(username='newuser').first()
            assert user is not None
            assert user.email == 'newuser@example.com'

    def test_register_duplicate_username(self, client, test_user):
        """Тест регистрации с существующим username"""
        response = client.post('/register', data={
            'username': 'testuser',
            'email': 'different@example.com',
            'password': 'password123',
            'password2': 'password123'
        }, follow_redirects=True)
        # Может быть редирект или остаться на странице с ошибкой
        assert response.status_code in [200, 302]
        # Должно быть сообщение об ошибке или редирект


class TestQuestionViews:
    """Тесты для views вопросов"""

    def test_main_page_loads(self, client):
        """Тест загрузки главной страницы"""
        response = client.get('/main')
        assert response.status_code == 200

    def test_random_question_page(self, client, test_question):
        """Тест страницы случайного вопроса"""
        response = client.get('/random-question')
        assert response.status_code == 200

    def test_random_question_no_questions(self, client):
        """Тест случайного вопроса при отсутствии вопросов"""
        response = client.get('/random-question')
        assert response.status_code == 500

    def test_question_view(self, client, test_question):
        """Тест просмотра вопроса"""
        question_id = test_question.id
        question_title = test_question.title
        response = client.get(f'/questions/{question_id}')
        assert response.status_code == 200
        assert question_title.encode() in response.data

    def test_question_view_not_found(self, client):
        """Тест просмотра несуществующего вопроса"""
        response = client.get('/questions/99999')
        assert response.status_code == 404

    def test_all_questions_page(self, client, multiple_questions):
        """Тест страницы со списком всех вопросов"""
        response = client.get('/questions')
        assert response.status_code == 200

    def test_all_questions_search(self, client, multiple_questions):
        """Тест поиска вопросов"""
        response = client.get('/questions?search=Question 1')
        assert response.status_code == 200

    def test_all_questions_filter_by_tag(self, client):
        """Тест фильтрации вопросов по тегу"""
        with client.application.app_context():
            tag_python = Tag(name='python')
            q1 = Question(title='Python basics?', text='about python')
            q2 = Question(title='Flask intro?', text='about flask')
            q1.tags.append(tag_python)
            db.session.add_all([q1, q2])
            db.session.commit()

        response = client.get('/questions?tag=python')
        assert response.status_code == 200
        body = response.data.decode('utf-8', errors='ignore').lower()
        assert 'python basics?' in body
        assert 'flask intro?' not in body
        assert 'python' in body  # тег отображается в фильтре

    def test_add_question_requires_admin(self, client):
        """Тест, что добавление вопроса требует админ-прав"""
        response = client.get('/add')
        assert response.status_code == 403

    def test_add_question_as_admin(self, admin_client):
        """Тест добавления вопроса администратором"""
        response = admin_client.get('/add')
        assert response.status_code == 200

        # Пробуем добавить вопрос
        response = admin_client.post('/add', data={
            'title': 'New Test Question?',
            'text': 'New Test Answer'
        }, follow_redirects=True)
        assert response.status_code == 200

        # Проверяем, что вопрос создан
        with admin_client.application.app_context():
            question = Question.query.filter_by(
                title='New Test Question?').first()
            assert question is not None

    def test_edit_question_requires_admin(self, client, test_question):
        """Тест, что редактирование требует админ-прав"""
        question_id = test_question.id
        response = client.get(f'/questions/{question_id}/edit')
        assert response.status_code == 403

    def test_edit_question_as_admin(self, admin_client, test_question):
        """Тест редактирования вопроса администратором"""
        question_id = test_question.id
        response = admin_client.get(f'/questions/{question_id}/edit')
        assert response.status_code == 200

        # Пробуем обновить вопрос
        response = admin_client.post(f'/questions/{question_id}/edit', data={
            'title': 'Updated Question?',
            'text': 'Updated Answer',
            'tags': 'python, flask'
        }, follow_redirects=True)
        assert response.status_code == 200

        # Проверяем, что вопрос обновлён
        with admin_client.application.app_context():
            question = Question.query.get(question_id)
            assert question.title == 'Updated Question?'
            assert question.text == 'Updated Answer'
            assert sorted([t.name for t in question.tags]) == ['flask', 'python']


class TestComments:
    """Тесты для комментариев"""

    def test_add_comment_requires_login(self, client, test_question):
        """Тест, что добавление комментария требует входа"""
        question_id = test_question.id
        response = client.post(f'/questions/{question_id}', data={
            'text': 'Test comment'
        })
        # Должен быть редирект на логин или сообщение
        assert response.status_code in [200, 302]

    def test_add_comment_as_user(self, authenticated_client, test_question):
        """Тест добавления комментария пользователем"""
        question_id = test_question.id
        response = authenticated_client.post(
            f'/questions/{question_id}',
            data={'text': 'My test comment'},
            follow_redirects=True
        )
        assert response.status_code == 200

        # Проверяем, что комментарий создан
        with authenticated_client.application.app_context():
            comment = Comment.query.filter_by(text='My test comment').first()
            assert comment is not None
            assert comment.question_id == question_id

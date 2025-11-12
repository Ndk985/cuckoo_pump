"""
Тесты для форм (WTForms валидация)
"""
import pytest
from cp_app.forms import (
    QuestionForm, LoginForm, RegistrationForm, CommentForm
)


class TestQuestionForm:
    """Тесты для формы вопроса"""

    def test_question_form_valid(self, client):
        """Тест валидной формы вопроса"""
        with client.application.app_context():
            form = QuestionForm(data={
                'title': 'What is Python?',
                'text': 'Python is a programming language'
            })
            assert form.validate() is True

    def test_question_form_missing_title(self, client):
        """Тест формы без title"""
        with client.application.app_context():
            form = QuestionForm(data={
                'text': 'Some answer'
            })
            assert form.validate() is False

    def test_question_form_missing_text(self, client):
        """Тест формы без text"""
        with client.application.app_context():
            form = QuestionForm(data={
                'title': 'Some question?'
            })
            assert form.validate() is False

    def test_question_form_empty(self, client):
        """Тест пустой формы"""
        with client.application.app_context():
            form = QuestionForm(data={})
            assert form.validate() is False


class TestLoginForm:
    """Тесты для формы логина"""

    def test_login_form_valid(self, client):
        """Тест валидной формы логина"""
        with client.application.app_context():
            form = LoginForm(data={
                'login': 'testuser',
                'password': 'password123'
            })
            assert form.validate() is True

    def test_login_form_missing_login(self, client):
        """Тест формы без login"""
        with client.application.app_context():
            form = LoginForm(data={
                'password': 'password123'
            })
            assert form.validate() is False

    def test_login_form_missing_password(self, client):
        """Тест формы без password"""
        with client.application.app_context():
            form = LoginForm(data={
                'login': 'testuser'
            })
            assert form.validate() is False


class TestRegistrationForm:
    """Тесты для формы регистрации"""

    def test_registration_form_valid(self, client):
        """Тест валидной формы регистрации"""
        with client.application.app_context():
            form = RegistrationForm(data={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'password123',
                'password2': 'password123'
            })
            assert form.validate() is True

    def test_registration_form_password_mismatch(self, client):
        """Тест формы с несовпадающими паролями"""
        with client.application.app_context():
            form = RegistrationForm(data={
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password': 'password123',
                'password2': 'different123'
            })
            assert form.validate() is False

    def test_registration_form_short_username(self, client):
        """Тест формы с коротким username"""
        with client.application.app_context():
            form = RegistrationForm(data={
                'username': 'ab',  # Меньше 3 символов
                'email': 'user@example.com',
                'password': 'password123',
                'password2': 'password123'
            })
            assert form.validate() is False

    def test_registration_form_missing_fields(self, client):
        """Тест формы с отсутствующими полями"""
        with client.application.app_context():
            form = RegistrationForm(data={
                'username': 'newuser'
            })
            assert form.validate() is False


class TestCommentForm:
    """Тесты для формы комментария"""

    def test_comment_form_valid(self, client):
        """Тест валидной формы комментария"""
        with client.application.app_context():
            form = CommentForm(data={
                'text': 'This is a test comment'
            })
            assert form.validate() is True

    def test_comment_form_empty(self, client):
        """Тест пустой формы комментария"""
        with client.application.app_context():
            form = CommentForm(data={})
            assert form.validate() is False

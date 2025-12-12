"""
Тесты для моделей (User, Question, Comment)
"""
import pytest
from cp_app import db
from cp_app.models import User, Question, Comment, Tag
from datetime import datetime


class TestUser:
    """Тесты для модели User"""

    def test_create_user(self, client):
        """Тест создания пользователя"""
        with client.application.app_context():
            user = User(
                username='newuser',
                email='newuser@example.com',
                is_admin=False
            )
            user.set_password('password123')
            db.session.add(user)
            db.session.commit()

            assert user.id is not None
            assert user.username == 'newuser'
            assert user.email == 'newuser@example.com'
            assert user.is_admin is False
            assert user.password_hash is not None

    def test_set_password(self, client):
        """Тест установки пароля"""
        with client.application.app_context():
            user = User(username='test', email='test@test.com')
            user.set_password('mypassword')

            assert user.password_hash != 'mypassword'
            assert user.password_hash is not None

    def test_check_password(self, client):
        """Тест проверки пароля"""
        with client.application.app_context():
            user = User(username='test', email='test@test.com')
            user.set_password('correctpass')

            assert user.check_password('correctpass') is True
            assert user.check_password('wrongpass') is False

    def test_user_unique_username(self, client):
        """Тест уникальности username"""
        with client.application.app_context():
            user1 = User(username='unique', email='user1@test.com')
            user1.set_password('pass')
            db.session.add(user1)
            db.session.commit()

            user2 = User(username='unique', email='user2@test.com')
            user2.set_password('pass')
            db.session.add(user2)

            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()

    def test_user_unique_email(self, client):
        """Тест уникальности email"""
        with client.application.app_context():
            user1 = User(username='user1', email='same@test.com')
            user1.set_password('pass')
            db.session.add(user1)
            db.session.commit()

            user2 = User(username='user2', email='same@test.com')
            user2.set_password('pass')
            db.session.add(user2)

            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()


class TestQuestion:
    """Тесты для модели Question"""

    def test_create_question(self, client):
        """Тест создания вопроса"""
        with client.application.app_context():
            question = Question(
                title='What is Python?',
                text='Python is a programming language'
            )
            db.session.add(question)
            db.session.commit()

            assert question.id is not None
            assert question.title == 'What is Python?'
            assert question.text == 'Python is a programming language'

    def test_question_unique_title(self, client):
        """Тест уникальности title"""
        with client.application.app_context():
            q1 = Question(title='Unique Title?', text='Answer 1')
            db.session.add(q1)
            db.session.commit()

            q2 = Question(title='Unique Title?', text='Answer 2')
            db.session.add(q2)

            with pytest.raises(Exception):  # IntegrityError
                db.session.commit()

    def test_question_to_dict(self, client):
        """Тест метода to_dict"""
        with client.application.app_context():
            question = Question(
                title='Test Question?',
                text='Test Answer'
            )
            tag = Tag(name='python')
            question.tags.append(tag)
            db.session.add(question)
            db.session.commit()

            data = question.to_dict()
            assert data['id'] == question.id
            assert data['title'] == 'Test Question?'
            assert data['text'] == 'Test Answer'
            assert data['tags'] == ['python']

    def test_question_from_dict(self, client):
        """Тест метода from_dict"""
        with client.application.app_context():
            question = Question(title='Old Title?', text='Old Answer')
            db.session.add(question)
            db.session.commit()

            question.from_dict({
                'title': 'New Title?',
                'text': 'New Answer'
            })

            assert question.title == 'New Title?'
            assert question.text == 'New Answer'

    def test_question_tags_relationship(self, client):
        """Тест связи вопроса с тегами"""
        with client.application.app_context():
            question = Question(title='Tagged?', text='Answer with tags')
            python_tag = Tag(name='python')
            flask_tag = Tag(name='flask')
            question.tags.extend([python_tag, flask_tag])

            db.session.add(question)
            db.session.commit()

            stored = Question.query.get(question.id)
            tag_names = sorted([t.name for t in stored.tags])
            assert tag_names == ['flask', 'python']


class TestComment:
    """Тесты для модели Comment"""

    def test_create_comment(self, client, test_user, test_question):
        """Тест создания комментария"""
        with client.application.app_context():
            # Сохраняем ID перед использованием
            user_id = test_user.id
            question_id = test_question.id

            comment = Comment(
                text='This is a test comment',
                user_id=user_id,
                question_id=question_id
            )
            db.session.add(comment)
            db.session.commit()

            assert comment.id is not None
            assert comment.text == 'This is a test comment'
            assert comment.user_id == user_id
            assert comment.question_id == question_id
            assert isinstance(comment.timestamp, datetime)

    def test_comment_relationships(self, client, test_user, test_question):
        """Тест связей комментария с User и Question"""
        with client.application.app_context():
            # Сохраняем ID перед использованием
            user_id = test_user.id
            question_id = test_question.id

            comment = Comment(
                text='Test comment',
                user_id=user_id,
                question_id=question_id
            )
            db.session.add(comment)
            db.session.commit()

            # Перезагружаем объекты в текущей сессии
            user = User.query.get(user_id)
            question = Question.query.get(question_id)

            assert comment.user == user
            assert comment.question == question
            assert comment in user.comments
            assert comment in question.comments

"""
Фикстуры для pytest тестов
"""
import pytest
import os
import tempfile

# Устанавливаем переменные окружения ДО импорта приложения
os.environ.setdefault('DATABASE_URI', 'sqlite:///:memory:')
os.environ.setdefault('SECRET_KEY', 'test-secret-key')

from cp_app import app, db
from cp_app.models import User, Question


@pytest.fixture(scope='function')
def client():
    """Создаёт тестового клиента Flask с временной БД"""
    # Используем временную SQLite БД для тестов
    db_fd, db_path = tempfile.mkstemp(suffix='.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['TESTING'] = True
    app.config['SECRET_KEY'] = 'test-secret-key'
    app.config['WTF_CSRF_ENABLED'] = False  # Отключаем CSRF для тестов

    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

    os.close(db_fd)
    os.unlink(db_path)


@pytest.fixture
def test_user(client):
    """Создаёт тестового пользователя"""
    with app.app_context():
        user = User(
            username='testuser',
            email='test@example.com',
            is_admin=False
        )
        user.set_password('testpass123')
        db.session.add(user)
        db.session.commit()
        # Сохраняем ID и другие атрибуты для безопасного использования
        user_data = {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'is_admin': user.is_admin
        }

    # Создаём простой объект с атрибутами
    class UserStub:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    return UserStub(**user_data)


@pytest.fixture
def test_admin(client):
    """Создаёт тестового администратора"""
    with app.app_context():
        admin = User(
            username='admin',
            email='admin@example.com',
            is_admin=True
        )
        admin.set_password('adminpass123')
        db.session.add(admin)
        db.session.commit()
        admin_data = {
            'id': admin.id,
            'username': admin.username,
            'email': admin.email,
            'is_admin': admin.is_admin
        }

    class UserStub:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    return UserStub(**admin_data)


@pytest.fixture
def test_question(client):
    """Создаёт тестовый вопрос"""
    with app.app_context():
        question = Question(
            title='Test Question?',
            text='Test Answer'
        )
        db.session.add(question)
        db.session.commit()
        question_data = {
            'id': question.id,
            'title': question.title,
            'text': question.text
        }

    class QuestionStub:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    return QuestionStub(**question_data)


@pytest.fixture
def multiple_questions(client):
    """Создаёт несколько тестовых вопросов"""
    with app.app_context():
        questions_data = []
        for i in range(15):
            question = Question(
                title=f'Question {i+1}?',
                text=f'Answer {i+1}'
            )
            db.session.add(question)
            questions_data.append({
                'id': None,  # Будет установлен после commit
                'title': question.title,
                'text': question.text
            })
        db.session.commit()
        # Обновляем ID после commit
        for i, q in enumerate(questions_data):
            q['id'] = Question.query.filter_by(title=q['title']).first().id

    class QuestionStub:
        def __init__(self, **kwargs):
            for k, v in kwargs.items():
                setattr(self, k, v)
    return [QuestionStub(**q) for q in questions_data]


@pytest.fixture
def authenticated_client(client, test_user):
    """Клиент с аутентифицированным пользователем"""
    # Логинимся через POST запрос
    client.post('/login', data={
        'login': test_user.username,
        'password': 'testpass123'
    }, follow_redirects=True)
    return client


@pytest.fixture
def admin_client(client, test_admin):
    """Клиент с аутентифицированным администратором"""
    # Логинимся через POST запрос
    client.post('/login', data={
        'login': test_admin.username,
        'password': 'adminpass123'
    }, follow_redirects=True)
    return client

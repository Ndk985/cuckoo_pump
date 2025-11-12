"""
Тесты для quiz функциональности
"""
import pytest
from cp_app import db
from cp_app.models import Question


class TestQuiz:
    """Тесты для квиза"""

    def test_quiz_start_page(self, client):
        """Тест страницы начала квиза"""
        response = client.get('/quiz/start')
        assert response.status_code == 200

    def test_quiz_begin(self, client, multiple_questions):
        """Тест начала квиза"""
        response = client.post('/quiz/begin', follow_redirects=True)
        assert response.status_code == 200

        # Проверяем, что в сессии есть quiz_ids
        with client.session_transaction() as sess:
            assert 'quiz_ids' in sess
            assert 'quiz_index' in sess
            assert 'quiz_correct' in sess
            assert 'quiz_total' in sess
            assert len(sess['quiz_ids']) == 10

    def test_quiz_begin_less_than_10_questions(self, client):
        """Тест начала квиза, когда вопросов меньше 10"""
        # Создаём только 5 вопросов
        with client.application.app_context():
            for i in range(5):
                question = Question(
                    title=f'Question {i+1}?',
                    text=f'Answer {i+1}'
                )
                db.session.add(question)
            db.session.commit()

        response = client.post('/quiz/begin', follow_redirects=True)
        assert response.status_code == 200

        with client.session_transaction() as sess:
            assert len(sess['quiz_ids']) == 5
            assert sess['quiz_total'] == 5

    def test_quiz_step(self, client, multiple_questions):
        """Тест шага квиза"""
        # Начинаем квиз
        client.post('/quiz/begin')

        # Переходим к первому вопросу
        response = client.get('/quiz/step/0')
        assert response.status_code == 200

    def test_quiz_reveal(self, client, multiple_questions):
        """Тест раскрытия ответа"""
        # Начинаем квиз
        client.post('/quiz/begin')

        # Раскрываем ответ на первом вопросе
        response = client.post('/quiz/reveal/0')
        assert response.status_code == 200

    def test_quiz_mark_answered(self, client, multiple_questions):
        """Тест отметки правильного ответа"""
        # Начинаем квиз
        client.post('/quiz/begin')

        # Отмечаем первый вопрос как отвеченный
        response = client.post(
            '/quiz/mark/0',
            data={'mark': 'answered'},
            follow_redirects=True
        )
        assert response.status_code == 200

        # Проверяем, что счётчик увеличился
        with client.session_transaction() as sess:
            assert sess['quiz_correct'] == 1
            assert 'quiz_answers' in sess
            assert sess['quiz_answers'][str(sess['quiz_ids'][0])] is True

    def test_quiz_mark_not_answered(self, client, multiple_questions):
        """Тест отметки неправильного ответа"""
        # Начинаем квиз
        client.post('/quiz/begin')

        # Отмечаем первый вопрос как неотвеченный
        response = client.post(
            '/quiz/mark/0',
            data={'mark': 'not_answered'},
            follow_redirects=True
        )
        assert response.status_code == 200

        # Проверяем, что счётчик не увеличился
        with client.session_transaction() as sess:
            assert sess['quiz_correct'] == 0
            assert 'quiz_answers' in sess
            assert (sess['quiz_answers'].get(str(sess['quiz_ids'][0]), False)
                    is False)

    def test_quiz_finish(self, client, multiple_questions):
        """Тест завершения квиза"""
        # Начинаем квиз
        client.post('/quiz/begin')

        # Отмечаем все вопросы как отвеченные
        with client.session_transaction() as sess:
            for i in range(sess['quiz_total']):
                client.post(f'/quiz/mark/{i}', data={'mark': 'answered'})

        # Завершаем квиз
        response = client.get('/quiz/finish')
        assert response.status_code == 200

        # Проверяем статистику
        with client.session_transaction() as sess:
            assert sess['quiz_correct'] == sess['quiz_total']

    def test_quiz_finish_shows_statistics(self, client, multiple_questions):
        """Тест, что финальная страница показывает статистику"""
        # Начинаем квиз
        client.post('/quiz/begin')

        # Отмечаем несколько вопросов
        client.post('/quiz/mark/0', data={'mark': 'answered'})
        client.post('/quiz/mark/1', data={'mark': 'answered'})
        client.post('/quiz/mark/2', data={'mark': 'not_answered'})

        # Завершаем квиз
        response = client.get('/quiz/finish')
        assert response.status_code == 200
        # Проверяем, что на странице есть информация о результатах
        assert (b'correct' in response.data.lower() or
                b'10' in response.data or b'2' in response.data)

    def test_quiz_reset(self, client, multiple_questions):
        """Тест сброса квиза"""
        # Начинаем квиз
        client.post('/quiz/begin')

        # Проверяем, что сессия заполнена
        with client.session_transaction() as sess:
            assert 'quiz_ids' in sess

        # Сбрасываем квиз
        response = client.post('/quiz/reset', follow_redirects=True)
        assert response.status_code == 200

        # Проверяем, что сессия очищена
        with client.session_transaction() as sess:
            assert 'quiz_ids' not in sess
            assert 'quiz_index' not in sess
            assert 'quiz_correct' not in sess

    def test_quiz_progression(self, client, multiple_questions):
        """Тест прохождения всего квиза"""
        # Начинаем квиз
        client.post('/quiz/begin')

        # Проходим все шаги
        with client.session_transaction() as sess:
            total = sess['quiz_total']

        for i in range(total):
            # Просматриваем вопрос
            response = client.get(f'/quiz/step/{i}')
            assert response.status_code == 200

            # Раскрываем ответ
            response = client.post(f'/quiz/reveal/{i}')
            assert response.status_code == 200

            # Отмечаем ответ
            if i < total - 1:
                response = client.post(
                    f'/quiz/mark/{i}', data={'mark': 'answered'},
                    follow_redirects=True
                )
            else:
                # Последний вопрос ведёт на финиш
                response = client.post(
                    f'/quiz/mark/{i}',
                    data={'mark': 'answered'},
                    follow_redirects=True
                )
                assert response.status_code == 200
                # Проверяем, что попали на финиш
                path_str = (response.request.path.lower() if
                            response.request.path else '')
                data_str = response.data.decode(
                    'utf-8', errors='ignore').lower()
                assert 'finish' in path_str or 'finish' in data_str

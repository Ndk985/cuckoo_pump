## Качаем кукуху 🧠⚡ Cuckoo Pump ##
Приложение для прокачки знаний перед собеседованиями по Python. Cлучайные карточки с вопросами, квиз для самопроверки + телеграм-бот.

**Автор**
Назарян Даниэл Комитасович
[GitHub](https://github.com/Ndk985)

## Что это ##
Веб-приложение на Flask, которое:
- показывает случайные вопросы по Python;
- позволяет админу добавлять/редактировать карточки через визуальный редактор CKEditor;
- отдаёт JSON-API для сторонних клиентов (в т.ч. Telegram-бота);
- содержит соло-квиз из 10 неповторяющихся вопросов с механизмом самооценки.

## Техно-стек ##
Python 3.9, Flask, SQLAlchemy, Alembic, SQLite, Bootstrap, python-telegram-bot

**Команды развертывания**
```bash
git clone https://github.com/YOUR_LOGIN/cuckoo_pump.git
cd cuckoo_pump
python -m venv venv
source venv/bin/activate  # venv\Scripts\activate
pip install -r requirements.txt
flask db upgrade
```

## Настройте переменные окружения ##
Файл .env (пример):
```bash
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///db.sqlite3
TG_BOT_TOKEN=123456:ABC   # если нужен Telegram-бот
```

**Команды запуска**
```bash
flask shell
>>> from cp_app import db, User
>>> u = User(username='admin', is_admin=True)
>>> u.set_password('very-secret')
>>> db.session.add(u); db.session.commit(); exit()
flask run
```

**Справка**
📂 Структура проекта

cp_app/
├── static/          # CSS, изображения, шрифты
├── templates/       # Jinja2-шаблоны
├── models.py        # User, Question
├── views.py         # веб-страницы
├── api_views.py     # REST-API
├── quiz.py          # квиз-соло (blueprint)
├── forms.py         # WTForms + CKEditor
└── __init__.py      # фабрика приложения

🧠 Квиз-соло (session-based)

Нажимаете «Начать квиз» → сервер формирует 10 уникальных ID и сохраняет их в session.
Поочерёдно показываются вопросы (только title).
После выбора «Знаю / Не знаю» появляется ответ (text).
Самооценка: «Ответил» (зелёная) или «Нужно подучить» (красная).
В конце — статистика X / 10 и кнопка «Пройти ещё раз».
Всё хранится в session, новых таблиц не требуется.

🎨 Оформление

Bootstrap 5 + кастомные цвета в style.css.
Шрифт Montserrat.
Через CKEditor можно вставлять код, списки, цитаты — при выводе всё превращается в красивый HTML-разметкой |markdown|safe.
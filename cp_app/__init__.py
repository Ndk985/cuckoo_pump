# cp_app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_ckeditor import CKEditor
from settings import Config
import markdown
from bleach import clean

# ------------------------------------------------------------------
# 0.  Создаём глобальные объекты расширений
# ------------------------------------------------------------------
db           = SQLAlchemy()
migrate      = Migrate()
ckeditor     = CKEditor()
login_manager = LoginManager()

# ------------------------------------------------------------------
# 1.  Создаём приложение
# ------------------------------------------------------------------
app = Flask(__name__)
app.config.from_object(Config)

# ------------------------------------------------------------------
# 2.  Инициализируем расширения
# ------------------------------------------------------------------
db.init_app(app)
migrate.init_app(app, db)
ckeditor.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице'

# ------------------------------------------------------------------
# 3.  Вспомогательные константы и фильтры
# ------------------------------------------------------------------
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'ul', 'ol', 'li',
    'pre', 'code', 'blockquote', 'h1', 'h2', 'h3',
    'h4', 'h5', 'h6', 'a'
]


def md_to_html(text: str) -> str:
    md = markdown.Markdown(
        extensions=['codehilite', 'fenced_code', 'tables']
    )
    html = md.convert(text)
    safe_html = clean(html, tags=ALLOWED_TAGS, strip=True)
    return safe_html


app.jinja_env.filters['markdown'] = md_to_html


# ------------------------------------------------------------------
# 4.  user_loader (нужен для Flask-Login)
# ------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    # импорт внутри функции, чтобы избежать кругового импорта
    from cp_app.models import User
    return User.query.get(int(user_id))

# ------------------------------------------------------------------
# 5.  Импортируем вьюхи/команды/обработчики ПОСЛЕ создания app
# ------------------------------------------------------------------
from cp_app import models   # noqa: E402
from cp_app import views    # noqa: E402
from cp_app.quiz import quiz_bp
app.register_blueprint(quiz_bp)
from cp_app import api_views, cli_commands, error_handlers  # noqa: E402

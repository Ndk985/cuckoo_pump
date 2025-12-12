# cp_app/__init__.py
from flask import Flask, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager, current_user
from flask_ckeditor import CKEditor
from settings import Config
import markdown
from bleach import clean

# ------------------------------------------------------------------
# Monkey patch: Flask-Admin + WTForms 3.x совместимость
# ------------------------------------------------------------------
import wtforms.fields.core as wt_core

if not hasattr(wt_core, "_patched_for_flask_admin"):
    original_init = wt_core.Field.__init__

    def patched_init(self, *args, **kwargs):
        # WTForms 3.x использует flags внутри args[1] или kwargs
        new_args = list(args)
        if len(new_args) > 1 and isinstance(new_args[1], tuple):
            # заменяем tuple на dict, чтобы .items() не падало
            new_args[1] = {str(i): f for i, f in enumerate(new_args[1])}
        elif "flags" in kwargs and isinstance(kwargs["flags"], tuple):
            kwargs["flags"] = {str(i): f for i, f in enumerate(kwargs["flags"])}
        original_init(self, *new_args, **kwargs)

    wt_core.Field.__init__ = patched_init
    wt_core._patched_for_flask_admin = True


# ------------------------------------------------------------------
# 1.  Создаём глобальные объекты расширений
# ------------------------------------------------------------------
db = SQLAlchemy()
migrate = Migrate()
ckeditor = CKEditor()
login_manager = LoginManager()

# ------------------------------------------------------------------
# 2.  Создаём приложение
# ------------------------------------------------------------------
app = Flask(__name__)
app.config.from_object(Config)

from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# ------------------------------------------------------------------
# 3.  Инициализируем расширения
# ------------------------------------------------------------------
db.init_app(app)
migrate.init_app(app, db)
ckeditor.init_app(app)
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Пожалуйста, войдите для доступа к этой странице'

# ------------------------------------------------------------------
# 4.  Вспомогательные константы и фильтры
# ------------------------------------------------------------------
ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'ul', 'ol', 'li',
    'pre', 'code', 'blockquote', 'h1', 'h2', 'h3',
    'h4', 'h5', 'h6', 'a'
]


def md_to_html(text: str) -> str:
    md = markdown.Markdown(extensions=['codehilite', 'fenced_code', 'tables'])
    html = md.convert(text)
    safe_html = clean(html, tags=ALLOWED_TAGS, strip=True)
    return safe_html


app.jinja_env.filters['markdown'] = md_to_html
app.jinja_env.filters['zip'] = zip

# ------------------------------------------------------------------
# 5.  user_loader (нужен для Flask-Login)
# ------------------------------------------------------------------
@login_manager.user_loader
def load_user(user_id):
    from cp_app.models import User
    return User.query.get(int(user_id))

# ------------------------------------------------------------------
# 6.  Импортируем вьюхи/команды/обработчики ПОСЛЕ создания app
# ------------------------------------------------------------------
from cp_app import models  # noqa: E402
from cp_app import views   # noqa: E402
from cp_app.quiz import quiz_bp
app.register_blueprint(quiz_bp)
from cp_app import api_views, cli_commands, error_handlers  # noqa: E402
from cp_app.models import Question


@app.context_processor
def inject_counts():
    count = Question.query.count()
    last_two = count % 100
    if 11 <= last_two <= 14:
        word = "вопросов"
    else:
        rem = count % 10
        if rem == 1:
            word = "вопрос"
        elif 2 <= rem <= 4:
            word = "вопроса"
        else:
            word = "вопросов"
    return dict(question_count=count, question_word=word)

# ------------------------------------------------------------------
# 7.  Flask-Admin: подключение административной панели
# ------------------------------------------------------------------
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from wtforms import PasswordField


# Кастомный класс ModelView, чтобы ограничить доступ только для админов
class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and getattr(current_user, "is_admin", False)

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('login', next=url_for('admin.index')))


# Создаём экземпляр админки
admin = Admin(app, name='Quiz Admin', template_mode='bootstrap4')

# Импортируем модели и регистрируем их
from cp_app.models import User, Question, Comment, Tag


# Кастомный ModelView для пользователей
class UserAdminView(AdminModelView):
    column_list = ('id', 'username', 'email', 'is_admin')
    column_searchable_list = ('username', 'email')
    column_filters = ('is_admin',)
    form_excluded_columns = ('password_hash', 'comments')

    form_extra_fields = {
        'password': PasswordField('Пароль')
    }

    def on_model_change(self, form, model, is_created):
        if form.password.data:
            model.set_password(form.password.data)


# Регистрируем модели в админке
admin.add_view(UserAdminView(User, db.session))
admin.add_view(AdminModelView(Question, db.session))
admin.add_view(AdminModelView(Comment, db.session))
admin.add_view(AdminModelView(Tag, db.session))

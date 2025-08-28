from flask import Flask
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from settings import Config
from flask_ckeditor import CKEditor
import markdown
from bleach import clean, linkify


ALLOWED_TAGS = [
    'p', 'br', 'strong', 'em', 'ul', 'ol', 'li', 'pre', 'code',
    'blockquote', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'a'
]

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
ckeditor = CKEditor(app)


def md_to_html(text: str) -> str:
    """Превращает Markdown в безопасный HTML."""
    md = markdown.Markdown(extensions=['codehilite', 'fenced_code', 'tables'])
    html = md.convert(text)
    safe_html = clean(html, tags=ALLOWED_TAGS, strip=True)
    return linkify(safe_html)

app.jinja_env.filters['markdown'] = md_to_html

from . import api_views, cli_commands, error_handlers, views

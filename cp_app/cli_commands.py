import csv

import click

from . import app, db
from .models import Question


@app.cli.command('load_questions')
def load_opinions_command():
    """Функция загрузки вопросов в базу данных."""
    with open('questions.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        counter = 0
        for row in reader:
            question = Question(**row)
            db.session.add(question)
            db.session.commit()
            counter += 1
    click.echo(f'Загружено мнений: {counter}')

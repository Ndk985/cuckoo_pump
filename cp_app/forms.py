from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, URLField
from wtforms.validators import DataRequired, Length, Optional


class QuestionForm(FlaskForm):
    title = StringField(
        'Введите вопрос',
        validators=[DataRequired(message='Обязательное поле'),
                    Length(1, 128)]
    )
    text = TextAreaField(
        'Напишите ответ',
        validators=[DataRequired(message='Обязательное поле')]
    )
    submit = SubmitField('Добавить')

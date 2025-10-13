from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, EmailField
from wtforms.validators import DataRequired, Length
from flask_ckeditor import CKEditorField
from wtforms import PasswordField, TextAreaField
from wtforms.validators import EqualTo


class QuestionForm(FlaskForm):
    title = StringField(
        'Введите вопрос',
        validators=[DataRequired(message='Обязательное поле'),
                    Length(1, 128)]
    )
    text = CKEditorField(
        'Напишите ответ',
        validators=[DataRequired(message='Обязательное поле')]
    )
    submit = SubmitField('Добавить')


class LoginForm(FlaskForm):
    login = StringField('Username или Email', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(3, 64)])
    email = EmailField('Email')
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль',
                              validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')


class CommentForm(FlaskForm):
    text = TextAreaField(
        'Комментарий',
        validators=[DataRequired()],
        render_kw={
            "class": "form-control",
            "rows": 4,
            "placeholder": "Напишите ваш комментарий..."
        }
    )
    submit = SubmitField('Отправить')

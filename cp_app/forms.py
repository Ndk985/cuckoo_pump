from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length
from flask_ckeditor import CKEditorField
from wtforms import PasswordField
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
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class RegistrationForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired(), Length(3, 64)])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password2 = PasswordField('Повторите пароль',
                              validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

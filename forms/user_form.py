from flask_wtf import FlaskForm
from wtforms import PasswordField, StringField, SubmitField, EmailField, IntegerField,  SelectMultipleField
from wtforms.validators import DataRequired


class UserForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия пользователя', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    like_genres_of_books = SelectMultipleField(
        choices=['Фэнтези', 'Фантастика', 'Детектив', 'Романтика', 'Наука', 'Психология'],
        label='Любимые жанры книг: ', validators=[DataRequired()],)
    submit = SubmitField('Зарегистрировать')

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import PasswordField, StringField, SubmitField, EmailField, IntegerField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, optional


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()


class UserForm(FlaskForm):
    email = EmailField('Почта', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    password_again = PasswordField('Повторите пароль', validators=[DataRequired()])
    surname = StringField('Фамилия пользователя', validators=[DataRequired()])
    name = StringField('Имя пользователя', validators=[DataRequired()])
    age = IntegerField('Возраст', validators=[DataRequired()])
    like_genres_of_books = MultiCheckboxField(
        choices=['Фэнтези', 'Фантастика', 'Детектив', 'Романтика', 'Наука', 'Психология'],
        label='Любимые жанры книг: ', validators=[DataRequired()],)

    file = FileField('Ваша аватарка', validators=[optional()])

    submit = SubmitField('Зарегистрировать')

    def __init__(self, button_text):
        super(UserForm, self).__init__()
        self.submit.name = button_text

from flask_wtf import FlaskForm
from flask_wtf.file import FileField
from wtforms import PasswordField, StringField, SubmitField, EmailField, IntegerField, SelectMultipleField, widgets
from wtforms.validators import DataRequired, optional
from data.db import db_session
from data.models.genres import Genre

db_session.global_init("data/db/db_files/explorer.sqlite")
db_sess = db_session.create_session()


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
    like_genres = MultiCheckboxField(
        choices=[genre.name for genre in db_sess.query(Genre).all()],
        label='Любимые жанры книг: ', validators=[optional()], )

    file = FileField('Ваша аватарка', validators=[optional()])

    submit = SubmitField('Зарегистрировать')

    def __init__(self, button_text):
        super(UserForm, self).__init__()
        self.submit.label.text = button_text

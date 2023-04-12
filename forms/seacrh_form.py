from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, RadioField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    user_text = StringField('Найти:', validators=[DataRequired()])
    people_or_books = RadioField(
        choices=['Человека', 'Книгу'],
        label='Кого хотите найти: ', validators=[DataRequired()], )
    submit = SubmitField('Найти')

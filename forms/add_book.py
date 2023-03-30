from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired


class BookForm(FlaskForm):
    title = StringField('Название книги', validators=[DataRequired()])
    genre = SelectField('Жанр', validators=[DataRequired()],
                        choices=['Фэнтези', 'Фантастика', 'Детектив', 'Романтика', 'Наука', 'Психология'])
    brief_retelling = TextAreaField('Краткий пересказ', validators=[DataRequired()])
    feedback = TextAreaField('Отзыв', validators=[DataRequired()])
    submit = SubmitField('Применить')

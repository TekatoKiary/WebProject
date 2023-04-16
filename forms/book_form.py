from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from data.db import db_session
from data.models.genres import Genre

db_session.global_init("data/db/db_files/explorer.sqlite")
db_sess = db_session.create_session()


class BookForm(FlaskForm):
    title = StringField('Название книги', validators=[DataRequired()])
    genre = SelectField('Жанр', validators=[DataRequired()],
                        choices=[genre.name for genre in db_sess.query(Genre).all()])
    brief_retelling = TextAreaField('Краткий пересказ', validators=[DataRequired()])
    feedback = TextAreaField('Отзыв', validators=[DataRequired()])
    submit = SubmitField('Применить')

    def __init__(self, button_text):
        super(BookForm, self).__init__()
        self.submit.label.text = button_text

import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from data.db.db_session import SqlAlchemyBase


class Book(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'books'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    title = sqlalchemy.Column(sqlalchemy.String)
    user_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    genre_id = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("genres.id"))

    brief_retelling = sqlalchemy.Column(sqlalchemy.Text, default='')
    feedback = sqlalchemy.Column(sqlalchemy.Text, default='')

    count_likes = sqlalchemy.Column(sqlalchemy.Integer, default=0)

    user = orm.relationship('User')
    genre = orm.relationship('Genre')

    def __init__(self, user_id, title, genre_id, brief_retelling='', feedback=''):
        self.user_id = user_id
        self.title = title
        self.genre_id = genre_id
        self.brief_retelling = brief_retelling
        self.feedback = feedback

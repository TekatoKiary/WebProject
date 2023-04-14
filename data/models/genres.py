import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from data.db.db_session import SqlAlchemyBase


class Genre(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'genres'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    name = sqlalchemy.Column(sqlalchemy.String)

    def __init__(self, genre_name):
        self.name = genre_name

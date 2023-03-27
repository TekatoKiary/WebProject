import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from data.db.db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    surname = sqlalchemy.Column(sqlalchemy.String)
    name = sqlalchemy.Column(sqlalchemy.String)
    age = sqlalchemy.Column(sqlalchemy.Integer)
    email = sqlalchemy.Column(sqlalchemy.String, unique=True)

    hashed_password = sqlalchemy.Column(sqlalchemy.String, default='')

    like_genres_of_books = sqlalchemy.Column(sqlalchemy.String, default='')
    # books = sqlalchemy.Column(sqlalchemy.String, default='')

    def __init__(self, surname, name, age, email, like_genres_of_books):
        self.surname = surname
        self.name = name
        self.age = age
        self.email = email
        self.like_genres_of_books = like_genres_of_books

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from data.db.db_session import SqlAlchemyBase


class User(SqlAlchemyBase, UserMixin, SerializerMixin):
    __tablename__ = 'users'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    surname = sqlalchemy.Column(sqlalchemy.String(collation='NOCASE'))
    name = sqlalchemy.Column(sqlalchemy.String(collation='NOCASE'))
    age = sqlalchemy.Column(sqlalchemy.Integer, default='')
    email = sqlalchemy.Column(sqlalchemy.String, unique=True, default='')

    hashed_password = sqlalchemy.Column(sqlalchemy.String, default='')

    like_genres = sqlalchemy.Column(sqlalchemy.String, default='')
    friends = sqlalchemy.Column(sqlalchemy.String, default='')
    favorites = sqlalchemy.Column(sqlalchemy.String, default='')

    def __init__(self, surname, name, age, email, like_genres, favorites=None, friends=None):
        self.surname = surname
        self.name = name
        self.age = age
        self.email = email
        self.like_genres = like_genres
        if favorites is not None:
            self.favorites = favorites
        if friends is not None:
            self.friends = friends

    def set_password(self, password):
        self.hashed_password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.hashed_password, password)

    def add_friend(self, ind):
        if ind in self.friends.split():
            return
        if self.friends:
            self.friends += ' ' + str(ind)
        else:
            self.friends = str(ind)

    def del_friend(self, ind):
        ind = str(ind).strip()
        self.friends = self.friends[:self.friends.index(ind)] + self.friends[self.friends.index(ind) + len(ind) + 1:]

    def add_favorite_book(self, ind):
        if ind in self.favorites.split():
            return
        if self.favorites:
            self.favorites += ' ' + str(ind)
        else:
            self.favorites = str(ind)

    def del_favorite_book(self, ind):
        ind = str(ind).strip()
        self.favorites = self.favorites[:self.favorites.index(ind)] + self.favorites[
                                                                      self.favorites.index(ind) + len(ind) + 1:]

    def add_like_genre(self, ind):
        if ind in self.like_genres.split():
            return
        if self.like_genres:
            self.like_genres += ' ' + str(ind)
        else:
            self.like_genres = str(ind)

    def del_like_genre(self, ind):
        ind = str(ind).strip()
        self.like_genres = self.like_genres[:self.like_genres.index(ind)] + self.like_genres[
                                                                            self.like_genres.index(ind) + len(ind) + 1:]

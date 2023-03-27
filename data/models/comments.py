import datetime

import sqlalchemy
from sqlalchemy_serializer import SerializerMixin
from sqlalchemy import orm
from data.db.db_session import SqlAlchemyBase


class Comment(SqlAlchemyBase, SerializerMixin):
    __tablename__ = 'comments'

    id = sqlalchemy.Column(sqlalchemy.Integer, primary_key=True, autoincrement=True)

    users_comment = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("users.id"))
    content_text = sqlalchemy.Column(sqlalchemy.String)
    books_comment = sqlalchemy.Column(sqlalchemy.Integer, sqlalchemy.ForeignKey("books.id"))
    datetime_create = sqlalchemy.Column(sqlalchemy.DateTime, default=datetime.datetime.now())

    user = orm.relationship('User')
    book = orm.relationship('Book')

    def __init__(self, users_comment, content_text, books_comment):
        self.users_comment = users_comment
        self.content_text = content_text
        self.books_comment = books_comment

from data.db import db_session
from data.models.books import Book
from data.models.users import User
from flask_restful import abort, Resource
from flask import jsonify
from data.parsers.books_parser import parser


def abort_if_book_not_found(book_id):
    session = db_session.create_session()
    book = session.query(Book).get(book_id)
    if not book:
        abort(404, message=f"Book {book_id} not found")


class BookResource(Resource):
    def get(self, book_id):
        abort_if_book_not_found(book_id)
        session = db_session.create_session()
        book = session.query(Book).get(book_id)
        return jsonify({'book': book.to_dict(
            only=('id', 'title', 'user_id', 'genre_id', 'brief_retelling', 'feedback'))})

    def delete(self, book_id):
        abort_if_book_not_found(book_id)
        session = db_session.create_session()
        book = session.query(Book).get(book_id)
        for user in session.query(User).filter(User.favorites.like(f'%{book_id}%')):
            favorites = user.favorites.split()
            del favorites[favorites.index(str(book_id))]
            user.favorites = ' '.join(favorites)
        session.delete(book)
        session.commit()
        return jsonify({'success': 'OK'})


class BooksListResource(Resource):
    def get(self):
        session = db_session.create_session()
        books = session.query(Book).all()
        return jsonify({'books': [item.to_dict(
            only=('id', 'title', 'user_id', 'genre_id', 'brief_retelling', 'feedback'))
            for item in books]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()

        book = Book(
            title=args['title'],
            user_id=args['user_id'],
            genre_id=args['genre_id'],
            brief_retelling=args['brief_retelling'],
            feedback=args['feedback'],
        )
        session.add(book)
        session.commit()
        return jsonify({'success': 'OK'})

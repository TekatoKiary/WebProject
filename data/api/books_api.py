from flask import Blueprint, jsonify
from data.db import db_session
from data.models.books import Book

blueprint = Blueprint(
    'books_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/books')
def get_books():
    db_sess = db_session.create_session()
    books = db_sess.query(Book).all()
    return jsonify(
        {
            'books':
                [item.to_dict(only=('id', 'title', 'user_id', 'genre_id', 'brief_retelling', 'feedback'))
                 for item in books]
        }
    )


@blueprint.route('/api/books/<int:book_id>', methods=['GET'])
def get_book(book_id):
    db_sess = db_session.create_session()
    book = db_sess.query(Book).get(book_id)
    if not book:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'book': book.to_dict(
                only=('id', 'title', 'user_id', 'genre_id', 'brief_retelling', 'feedback'))
        }
    )

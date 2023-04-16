from data.db import db_session
from data.models.users import User
from data.models.books import Book
from flask_restful import abort, Resource
from flask import jsonify
from data.parsers.users_parser import parser


def abort_if_user_not_found(user_id):
    session = db_session.create_session()
    user = session.query(User).get(user_id)
    if not user:
        abort(404, message=f"User {user_id} not found")


class UserResource(Resource):
    def get(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        return jsonify({'user': user.to_dict(
            only=('id', 'surname', 'name', 'age', 'email', 'hashed_password', 'like_genres', 'friends',
                  'favorites'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)

        for friend in session.query(User).filter(User.friends.like(f'%{user_id}%')):
            friends = friend.friends.split()
            del friends[friends.index(str(user_id))]
            friend.friends = ' '.join(friends)

        for book in session.query(Book).filter(Book.user_id == user_id):
            book.user_id = -1

        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=('id', 'surname', 'name', 'age', 'email', 'hashed_password', 'like_genres', 'friends', 'favorites'))
            for item in users]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()

        if type(args['friends']) == list:
            friends = ', '.join(args['friends'])
        else:
            friends = args['friends']
        if type(args['favorites']) == list:
            favorites = ', '.join(args['favorites'])
        else:
            favorites = args['favorites']
        if type(args['like_genres']) == list:
            like_genres = ', '.join(args['like_genres'])
        else:
            like_genres = args['like_genres']

        user = User(
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            favorites=favorites,
            friends=friends,
            like_genres=like_genres,
            email=args['email'],
        )
        user.set_password(args['hashed_password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})

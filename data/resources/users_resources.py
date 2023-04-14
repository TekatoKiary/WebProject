from data.db import db_session
from data.models.users import User
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
            only=('id', 'surname', 'name', 'age', 'email', 'hashed_password', 'like_genres_of_books', 'friends',
                  'favorites'))})

    def delete(self, user_id):
        abort_if_user_not_found(user_id)
        session = db_session.create_session()
        user = session.query(User).get(user_id)
        session.delete(user)
        session.commit()
        return jsonify({'success': 'OK'})


class UsersListResource(Resource):
    def get(self):
        session = db_session.create_session()
        users = session.query(User).all()
        return jsonify({'users': [item.to_dict(
            only=(
                'id', 'surname', 'name', 'age', 'email', 'hashed_password', 'like_genres_of_books', 'friends',
                'favorites'))
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
        if type(args['like_genres_of_books']) == list:
            like_genres_of_books = ', '.join(args['like_genres_of_books'])
        else:
            like_genres_of_books = args['like_genres_of_books']

        user = User(
            surname=args['surname'],
            name=args['name'],
            age=args['age'],
            favorites=favorites,
            friends=friends,
            like_genres_of_books=like_genres_of_books,
            email=args['email'],
        )
        user.set_password(args['hashed_password'])
        session.add(user)
        session.commit()
        return jsonify({'success': 'OK'})

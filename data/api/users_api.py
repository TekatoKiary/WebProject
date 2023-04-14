from flask import Blueprint, jsonify
from data.db import db_session
from data.models.users import User

blueprint = Blueprint(
    'users_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/users')
def get_users():
    db_sess = db_session.create_session()
    users = db_sess.query(User).all()
    return jsonify(
        {
            'users':
                [item.to_dict(only=('id', 'surname', 'name', 'age', 'email', 'hashed_password', 'like_genres_of_books',
                                    'friends', 'favorites'))
                 for item in users]
        }
    )


@blueprint.route('/api/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    db_sess = db_session.create_session()
    user = db_sess.query(User).get(user_id)
    if not user:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'user': user.to_dict(
                only=('id', 'surname', 'name', 'age', 'email', 'hashed_password', 'like_genres_of_books', 'friends',
                      'favorites'))
        }
    )

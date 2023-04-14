from flask import Blueprint, jsonify
from data.db import db_session
from data.models.genres import Genre

blueprint = Blueprint(
    'genres_api',
    __name__,
    template_folder='templates'
)


@blueprint.route('/api/genres')
def get_genres():
    db_sess = db_session.create_session()
    genres = db_sess.query(Genre).all()
    return jsonify(
        {
            'genres':
                [item.to_dict(only=('id', 'name'))
                 for item in genres]
        }
    )


@blueprint.route('/api/genres/<int:genre_id>', methods=['GET'])
def get_genre(genre_id):
    db_sess = db_session.create_session()
    genre = db_sess.query(Genre).get(genre_id)
    if not genre:
        return jsonify({'error': 'Not found'})
    return jsonify(
        {
            'genre': genre.to_dict(
                only=('id', 'name'))
        }
    )

from data.db import db_session
from data.models.genres import Genre
from flask_restful import abort, Resource
from flask import jsonify
from data.parsers.genres_parser import parser


def abort_if_genre_not_found(genre_id):
    session = db_session.create_session()
    genre = session.query(Genre).get(genre_id)
    if not genre:
        abort(404, message=f"Genre {genre_id} not found")


class GenreResource(Resource):
    def get(self, genre_id):
        abort_if_genre_not_found(genre_id)
        session = db_session.create_session()
        genre = session.query(Genre).get(genre_id)
        return jsonify({'genre': genre.to_dict(only=('id', 'name'))})

    def delete(self, genre_id):
        abort_if_genre_not_found(genre_id)
        session = db_session.create_session()
        genre = session.query(Genre).get(genre_id)
        session.delete(genre)
        session.commit()
        return jsonify({'success': 'OK'})


class GenresListResource(Resource):
    def get(self):
        session = db_session.create_session()
        genres = session.query(Genre).all()
        return jsonify({'genres': [item.to_dict(only=('id', 'name')) for item in genres]})

    def post(self):
        args = parser.parse_args()
        session = db_session.create_session()

        genre = Genre(genre_name=args['name'])

        session.add(genre)
        session.commit()
        return jsonify({'success': 'OK'})

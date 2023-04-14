from flask_restful import reqparse

parser = reqparse.RequestParser()
parser.add_argument('title', required=True)
parser.add_argument('user_id', required=True, type=int)
parser.add_argument('genre_id', required=True, type=int)
parser.add_argument('brief_retelling', required=True)
parser.add_argument('feedback', required=True)

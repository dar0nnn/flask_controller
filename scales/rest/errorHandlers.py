from flask import jsonify, make_response
from . import api

'''Описание ошибок для сервера'''

@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

@api.errorhandler(400)
def bad_req(error):
    return make_response(jsonify({'error': 'Bad request'}), 400)

@api.errorhandler(500)
def serv_error(error):
    return make_response(jsonify({'error': 'Server error'}), 500)
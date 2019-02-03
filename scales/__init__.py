# -*- coding: utf-8 -*-
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask.logging import default_handler
from instance.config import app_config
import logging

db = SQLAlchemy()
# логгер с добавлением логгера из фласка
LOG_FORMAT = '%(levelname)s, %(asctime)s - %(message)s'
logging.basicConfig(filename = 'poligons.log', filemode='a', format=LOG_FORMAT, level=logging.DEBUG)
logger = logging.getLogger()
logger.addHandler(default_handler)
logging.getLogger('urllib3').setLevel(logging.CRITICAL)
logging.getLogger("requests").setLevel(logging.CRITICAL)


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py') 
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    from scales.rest import api
    app.register_blueprint(api)

    return app

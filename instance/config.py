import os


class Config(object):
    DEBUG = False
    CSRF_ENABLED = False
    SECRET = 'secret'
    SQLALCHEMY_DATABASE_URI = 'postgres://postgres:1@localhost:5432/scales'
    HOST_NAME = 'conn center 1'
    NEIGHBOURS = [{"conn center 2": "http://192.168.229.129:5005"}]

class DevelopmentConfig(Config):
    DEBUG = True


class TestingConfig(Config):
    """для тестов, отдельная базка"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:1@localhost:5432/test_scales'
    DEBUG = True


class ProductionConfig(Config):
    """для полноценного запуска"""
    DEBUG = False
    TESTING = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
}

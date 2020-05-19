import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = True
    TESTING = False
    CSRF_ENABLED = True
    SECRET_KEY = os.getenv("NEWS_SRC_MS_SEC_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("NEWS_SRC_MS_DB_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    LOG_TO_STDOUT = os.getenv("LOG_TO_STDOUT")


class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TESTING = False
    DEVELOPMENT = False
    SECRET_KEY = os.urandom(24)
    LOG_TO_STDOUT = os.getenv("LOG_TO_STDOUT")


class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True


class TestingConfig(Config):
    TESTING = True

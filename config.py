import os
basedir = os.path.abspath(os.path.dirname(__file__))




class Config:
  DEBUG = True
  TESTING = False
  CSRF_ENABLED = True
  SECRET_KEY = os.getenv('NEWS_SRC_MS_SEC_KEY')
  SQLALCHEMY_DATABASE_URI = os.getenv('NEWS_SRC_MS_DB_URL')
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  # JOBS = [
  #     {
  #         'id': 'sift_1',
  #         'func': SourceController.sift_sources,
  #         'trigger': 'interval',
  #         'minutes': 2
  #     }
  # ]
  #
  # SCHEDULER_API_ENABLED = True

class ProductionConfig(Config):
    DEBUG = False

class StagingConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class DevelopmentConfig(Config):
    DEVELOPMENT = True
    DEBUG = True

class TestingConfig(Config):
    TESTING = True
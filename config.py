import os 
basedir = os.path.abspath(os.path.dirname(__file__))

class Config():
  SECRET_KEY = os.environ.get('SECRET_KEY')
  SQLALCHEMY_TRACK_MODIFICATIONS = False

  @staticmethod
  def init_app(app):
    pass

class DevelopmentConfig(Config):
  DEBUG = True
  SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,'data-dev.sqlite')
  DRAWING_IMAGES = '/home/runner/drawality/drawify/app/static/drawing_images'

class TestingConfig(Config):
  TESTING = True
  WTF_CSRF_ENABLED = False
  SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,'data-test.sqlite')

class ProductionConfig(Config):
  SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir,'data.sqlite')

config = {
  'development' : DevelopmentConfig,
  'testing': TestingConfig,
  'production': ProductionConfig,
  'default': DevelopmentConfig
}
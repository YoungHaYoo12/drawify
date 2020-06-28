from config import config 
from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'auth.login'

def create_app(config_name='default'):
  app = Flask(__name__)
  app.config.from_object(config[config_name])
  config[config_name].init_app(app)

  # Initialize Flask Extension Instances 
  db.init_app(app)
  login_manager.init_app(app)

  # Register blueprints
  from app.core import core as core_blueprint
  from app.auth import auth as auth_blueprint
  from app.drawings import drawings as drawings_blueprint

  app.register_blueprint(core_blueprint)
  app.register_blueprint(auth_blueprint,url_prefix='/auth')
  app.register_blueprint(drawings_blueprint,url_prefix='/drawings')

  return app
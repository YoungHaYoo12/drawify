from flask import Blueprint

games = Blueprint('games',__name__)

from app.games import views
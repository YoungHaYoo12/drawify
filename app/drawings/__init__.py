from flask import Blueprint

drawings = Blueprint('drawings',__name__)

from app.drawings import views
from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired

class AddGameForm(FlaskForm):
  max_points = IntegerField('Max Points',validators=[DataRequired()])
  submit = SubmitField('Create Game')
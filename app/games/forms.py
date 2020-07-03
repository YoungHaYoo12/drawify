from flask_wtf import FlaskForm
from wtforms import IntegerField, SubmitField
from wtforms.validators import DataRequired,NumberRange

class AddGameForm(FlaskForm):
  max_points = IntegerField('Max Points',validators=[DataRequired(),NumberRange(min=1, max=20, message='Max Points Not In Valid Number Range')])
  submit = SubmitField('Create Game')
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Length

class QuestionForm(FlaskForm):
  answer = StringField('Answer',validators=[DataRequired(), Length(min=0,max=64)])
  submit = SubmitField('Submit')
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField,SubmitField
from wtforms.validators import DataRequired, Length

class QuestionForm(FlaskForm):
  answer = StringField('Answer',validators=[DataRequired(), Length(min=0,max=64)])
  max_tries = IntegerField('Max Number of Tries')
  submit = SubmitField('Submit')

class QuestionAnswerForm(FlaskForm):
  answer = StringField('Answer',validators=[DataRequired(),Length(min=0,max=64)])
  submit = SubmitField('Submit')
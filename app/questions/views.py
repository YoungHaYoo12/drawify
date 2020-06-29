from app import db
from app.questions import questions
from app.questions.forms import QuestionForm
from app.models import Question,User,Drawing
from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, flash, abort
from datetime import datetime

@questions.route('/send_question/<recipient>/<drawing_id>',methods=['GET','POST'])
@login_required
def send_question(recipient,drawing_id):
  user = User.query.filter_by(username=recipient).first_or_404()
  drawing = Drawing.query.get_or_404(drawing_id)

  # validate user's drawing
  if not drawing in current_user.drawings.all():
    abort(403)

  # FOLLOWER RELATIONSHIP

  form = QuestionForm()

  if form.validate_on_submit():
    # Update user questions count notification
    user.add_notifications('unread_question_count',user.new_questions())
    db.session.commit()

    # add new Question instance
    question = Question(author=current_user, recipient=user,answer=form.answer.data,drawing=drawing)
    db.session.add(question)
    db.session.commit()
    flash('Your question has been sent.')
    return redirect(url_for('core.index'))

  return render_template('questions/send_question.html',form=form,recipient=recipient)

@questions.route('/questions')
@login_required
def questions():
  # update last time user read questions
  current_user.last_question_read_time = datetime.utcnow()
  db.session.commit()

  # load and render questions
  questions = current_user.questions_received.order_by(Question.timestamp.desc()).all()

  return render_template('questions/questions.html', questions=questions)
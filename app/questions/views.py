from app import db
from app.questions import questions
from app.questions.forms import QuestionForm, QuestionAnswerForm,HintForm
from app.models import Question,User,Drawing, Hint, Game
from flask_login import login_required, current_user
from flask import render_template, redirect, url_for, flash, abort
from datetime import datetime

@questions.route('/send_question/<recipient>/<drawing_id>/<game_id>',methods=['GET','POST'])
@login_required
def send_question(recipient,drawing_id,game_id):
  user = User.query.filter_by(username=recipient).first_or_404()
  drawing = Drawing.query.get_or_404(drawing_id)
  game = Game.query.get_or_404(game_id)

  # validate user's drawing
  if not drawing in current_user.drawings.all():
    abort(403)
  
  # validate game
  if not game.validate_players(current_user,user):
    abort(403)

  # Check if current user's turn
  if not game.is_turn(current_user):
    flash('It is currently not your turn.')
    return redirect(url_for('games.game',game_id=game.id))
  
  # check if game is in progress
  if not game.status == 'in_progress':
    flash('Game is currently not in progress.')
    return redirect(url_for('games.game',game_id=game.id))

  form = QuestionForm()

  if form.validate_on_submit():
    # Update user questions count notification
    user.add_notifications('unread_question_count',user.new_questions())
    db.session.commit()

    # update game
    if game.is_author(current_user):
      game.turn = 'waiting_guest_answer'
    else:
      game.turn = 'waiting_author_answer'

    # add new Question instance
    question = Question(author=current_user, recipient=user,answer=form.answer.data,drawing=drawing)
    if form.max_tries.data:
      question.max_tries = form.max_tries.data
    question.game = game
    db.session.add(question)
    db.session.commit()
    flash('Your question has been sent.')
    return redirect(url_for('games.game',game_id=question.game.id))

  return render_template('questions/send_question.html',form=form,recipient=recipient)

@questions.route('/send_hint/<question_id>',methods=['GET','POST'])
@login_required
def send_hint(question_id):
  # retrieve and validate question
  question = Question.query.get_or_404(question_id)
  if not question in current_user.questions_sent.all():
    abort(403)
  
  # form processing
  form = HintForm()

  if form.validate_on_submit():
    hint = Hint(body=form.body.data,question=question)
    db.session.add(hint)
    db.session.commit()
    flash('Hint Successfully Submitted')
    return redirect(url_for('questions.question',id=question.id))

  return render_template('questions/send_hint.html',form=form)

@questions.route('/list')
@login_required
def list():
  # get all new questions 
  new_questions_content = current_user.new_questions_content()

  # update last time user read questions
  current_user.last_question_read_time = datetime.utcnow()
  db.session.commit()

  return render_template('questions/list.html', new_questions_content=new_questions_content)

@questions.route('/question/<int:id>',methods=['GET','POST'])
@login_required
def question(id):
  # retrieve and validate question and game
  question = Question.query.get_or_404(id)
  game = question.game
  if not question in current_user.questions_received.all() and not question in current_user.questions_sent.all():
    abort(403)
  
  # form processing
  form = QuestionAnswerForm()

  if form.validate_on_submit() and question.status == 'in_progress' and question in current_user.questions_received.all():
    # increment question num of tries
    question.num_of_tries = question.num_of_tries + 1
    db.session.commit()

    # if question answered correctly
    if question.check_answer(form.answer.data):
      flash('Question Answered Correctly')
      question.status = 'complete'
      # update game
      game.make_user_turn(current_user)
      game.update_user_score(current_user,1)

      # check if game has been won
      if game.is_author_win():
        game.status = 'author'
        flash('Author Has Won!')
      if game.is_guest_win():
        game.status = 'guest'
        flash('Guest Has Won!')

      db.session.commit()

    # if question lost
    elif question.check_lost():
      flash('Incorrect. You Have Run Out of Tries On This Question')
      question.status = 'lost'
      # update game
      game.make_user_turn(current_user)

      db.session.commit()

    else:
      flash('Incorrect. Please Try Again.')

    return redirect(url_for('questions.question',id=question.id))

  return render_template('questions/question.html',form=form,question=question)
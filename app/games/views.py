from app import db
from app.games import games
from app.games.forms import AddGameForm
from app.models import User, Game, Question
from flask import render_template, redirect, url_for,flash,abort
from flask_login import login_required, current_user

@games.route('/game/<int:game_id>')
@login_required
def game(game_id):
  # retrieve and validate game
  game = Game.query.get_or_404(game_id)
  if current_user != game.author and current_user != game.guest:
    abort(403)
  
  questions = game.questions.order_by(Question.id.desc()).all()
  
  return render_template('games/game.html',game=game,questions=questions)

@games.route('/list')
@login_required
def list():
  created_games = current_user.created_games.all()
  invited_games = current_user.invited_games.all()

  return render_template('games/list.html',created_games=created_games,invited_games=invited_games)

@games.route('/pending_invites')
@login_required
def pending_invites():
  unconfirmed_games = current_user.unconfirmed_games()
  return render_template('games/pending_invites.html',unconfirmed_games=unconfirmed_games)

@games.route('/pending_answers')
@login_required
def pending_answers():
  unanswered_games = current_user.unanswered_games()
  return render_template('games/pending_answers.html',unanswered_games=unanswered_games)

@games.route('/send_invite/<opponent_username>',methods=['GET','POST'])
@login_required
def send_invite(opponent_username):
  opponent = User.query.filter_by(username=opponent_username).first_or_404()

  # form processing 
  form = AddGameForm()

  if form.validate_on_submit():
    game = Game(author=current_user,
                guest=opponent,
                max_points=form.max_points.data,)
    db.session.add(game)
    db.session.commit()
    flash('Game Invitation Sent')
    return redirect(url_for('core.user',username=opponent_username))
  
  return render_template('games/send_invite.html',form=form,opponent=opponent)

@games.route('/accept_invite/<int:game_id>')
@login_required
def accept_invite(game_id):
  # retrieve and validate game
  game = Game.query.get_or_404(game_id)

  # if user is not the game guest
  if current_user != game.guest:
    flash('You have not been invited to the following game.')
    return redirect(url_for('core.user',username=current_user.username))

  # if game is not 'not_confirmed'
  if game.status != 'not_confirmed':
    flash('The current game is not awaiting confirmation.')
    return redirect(url_for('core.user',username=current_user.username))
  
  # accept game
  game.status = 'in_progress'
  db.session.commit()

  return redirect(url_for('core.user',username=game.author.username))

@games.route('/reject_invite/<int:game_id>')
@login_required
def reject_invite(game_id):
  # retrieve and validate game
  game = Game.query.get_or_404(game_id)

  # if user is not the game guest
  if current_user != game.guest:
    flash('You have not been invited to the following game.')
    return redirect(url_for('core.user',username=current_user.username))

  # if game is not 'not_confirmed'
  if game.status != 'not_confirmed':
    flash('The current game is not awaiting confirmation.')
    return redirect(url_for('core.user',username=current_user.username))
  
  # reject game
  game.status = 'rejected'
  db.session.commit()

  return redirect(url_for('core.user',username=game.author.username))
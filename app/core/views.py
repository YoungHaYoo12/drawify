from flask import render_template, request,jsonify,flash, redirect,url_for
from flask_login import login_required, current_user
from app import db
from app.core import core
from app.models import Notification,User

@core.route('/')
def index():
  return render_template('core/index.html')

@core.route('/user/<username>')
@login_required
def user(username):
  user = User.query.filter_by(username=username).first_or_404()

  return render_template('core/user.html',user=user)

@core.route('/notifications')
@login_required
def notifications():
  since = request.args.get('since',0.0,type=float)
  notifications = current_user.notifications.filter(Notification.timestamp > since).order_by(Notification.timestamp.asc())

  return jsonify([{
        'name': n.name,
        'data': n.get_data(),
        'timestamp': n.timestamp
    } for n in notifications])

@core.route('/follow/<username>')
@login_required
def follow(username):
  user = User.query.filter_by(username=username).first()
  if user is None:
    flash('Invalid User')
    return redirect(url_for('core.index'))
  if current_user.is_following(user):
    flash('You are already following this user.')
    return redirect(url_for('core.user',username=username))
  current_user.follow(user)
  db.session.commit()
  flash(f"You are now following {username}")
  return redirect(url_for('core.user',username=username))

@core.route('/unfollow/<username>')
@login_required
def unfollow(username):
  user = User.query.filter_by(username=username).first()
  if user is None:
    flash('Invalid User')
    return redirect(url_for('core.index'))
  if not current_user.is_following(user):
    flash('You are currently not following this user.')
    return redirect(url_for('core.user',username=username))
  current_user.unfollow(user)
  db.session.commit()
  flash(f"You are no longer following {username}")
  return redirect(url_for('core.user',username=username))
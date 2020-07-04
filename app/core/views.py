from flask import render_template, request,jsonify,flash, redirect,url_for
from flask_login import login_required, current_user
from app import db
from app.core import core
from app.models import Notification,User,Drawing

@core.route('/')
def index():
  return render_template('core/index.html')

@core.route('/user/<username>')
@login_required
def user(username):
  page = request.args.get('page',1,type=int)
  user = User.query.filter_by(username=username).first_or_404()
  pagination = user.drawings.filter(Drawing.display==True).order_by(Drawing.timestamp.desc()).paginate(page=page,per_page=9)
  drawings = pagination.items

  return render_template('core/user.html',user=user,pagination=pagination,drawings=drawings)

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

@core.route('/send_friend_request/<username>')
@login_required
def send_friend_request(username):
  # retrieve and validate user
  user = User.query.filter_by(username=username).first()
  if user is None:
    flash('Invalid User')
    return redirect(url_for('core.index'))

  # Sent friend request to if appropriate
  if current_user.is_friends_with(user):
    flash('You Are Already Friends With This User')
  elif current_user.sent_friend_request_to(user):
    flash('You Have Already Sent a Friend Request to This User')
  elif current_user.received_friend_request_from(user):
    flash('You Have Already Received A Friend Request From This User')
  else:
    current_user.send_friend_request_to(user)
    flash('Successfully Sent Friend Request to User')
  return redirect(url_for('core.user',username=username))

@core.route('/accept_friend_request/<username>')
@login_required
def accept_friend_request(username):
  # retrieve and validate user
  user = User.query.filter_by(username=username).first()
  if user is None:
    flash('Invalid User')
    return redirect(url_for('core.index'))
  
  # accept friend request if appropriate
  if current_user.received_friend_request_from(user):
    current_user.accept_friend_request_from(user)
    flash('Successfully Accepted Friend Request')
  else:
    flash('You Currently Do Not Have a Friend Request from This User')

  return redirect(url_for('core.user',username=username))    

@core.route('/remove_friend/<username>')
@login_required
def remove_friend(username):
  # retrieve and validate user 
  user = User.query.filter_by(username=username).first()
  if user is None:
    flash('Invalid User')
    return redirect(url_for('core.index'))
  
  # remove friend if appropriate 
  if current_user.is_friends_with(user):
    current_user.remove_friend(user)
  else:
    flash('You Are Currently Not Friends with this User')
  
  return redirect(url_for('core.user',username=username))
  
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
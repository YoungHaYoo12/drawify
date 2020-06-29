from flask import render_template, request,jsonify
from flask_login import login_required, current_user
from app.core import core
from app.models import Notification

@core.route('/')
def index():
  return render_template('core/index.html')

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
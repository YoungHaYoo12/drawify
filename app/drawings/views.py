from flask import render_template,session,request,jsonify
from flask_login import current_user, login_required
from app import db
from app.drawings import drawings
from app.images import save_image
from app.models import User, Drawing

@drawings.route('/list/<username>')
@login_required
def list(username):
  user = User.query.filter_by(username=username).first_or_404()
  drawings = user.drawings.all()

  return render_template('drawings/list.html',drawings=drawings,user=user)

@drawings.route('/draw')
@login_required
def draw():
  return render_template('drawings/draw.html')

@drawings.route('/add',methods=['POST'])
@login_required
def add():
  if request.form['dataURL']:
    filename = save_image(request.form['dataURL'])
    drawing = Drawing(filename)
    drawing.user = current_user
    db.session.add(drawing)
    db.session.commit()

  return jsonify({
    'result':'success',
  })
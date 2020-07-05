from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from time import time
import json

class Friendship(db.Model):
  __tablename__ = 'friendships'
  inviter_id = db.Column(db.Integer, db.ForeignKey('users.id'),primary_key=True)
  invitee_id = db.Column(db.Integer, db.ForeignKey('users.id'),primary_key=True)
  status = db.Column(db.Enum('not_confirmed','confirmed'),nullable=False,server_default="not_confirmed")
  timestamp = db.Column(db.DateTime, default=datetime.utcnow)
  inviter_games_won = db.Column(db.Integer, default=0)
  invitee_games_won = db.Column(db.Integer, default=0)

  def get_friend(self,user):
    if self.inviter == user:
      return self.invitee
    else:
      return self.inviter

class User(db.Model,UserMixin):
  __tablename__ = 'users'
  id = db.Column(db.Integer,primary_key=True)
  username = db.Column(db.String(64),unique=True,index=True)
  email = db.Column(db.String(64),unique=True,index=True)
  password_hash = db.Column(db.String(128))
  drawings = db.relationship('Drawing',backref='user',lazy='dynamic',cascade="all, delete-orphan")
  notifications = db.relationship('Notification',backref='user',lazy='dynamic')

  questions_sent = db.relationship('Question',foreign_keys='Question.sender_id',backref='author',lazy='dynamic',cascade="all, delete-orphan")
  questions_received = db.relationship('Question',foreign_keys='Question.recipient_id',backref='recipient',lazy='dynamic',cascade="all, delete-orphan")
  last_question_read_time = db.Column(db.DateTime)

  created_games = db.relationship('Game',foreign_keys='Game.author_id',backref='author',lazy='dynamic',cascade="all, delete-orphan")
  invited_games = db.relationship('Game',foreign_keys='Game.guest_id',backref='guest',lazy='dynamic',cascade="all, delete-orphan")

  # Friends Functionality
  invitees = db.relationship('Friendship',
                              foreign_keys=[Friendship.inviter_id],
                              backref=db.backref('inviter',lazy='joined'),
                              lazy='dynamic',
                              cascade='all, delete-orphan')
  inviters = db.relationship('Friendship',
                              foreign_keys=[Friendship.invitee_id],
                              backref=db.backref('invitee',lazy='joined'),
                              lazy='dynamic',
                              cascade='all, delete-orphan')

  def friends(self):
    return self.invitees.union(self.inviters).filter_by(status='confirmed')

  def pending_friend_requests(self):
    return self.inviters.filter_by(status='not_confirmed')

  def pending_friend_requests_count(self):
    return self.inviters.filter_by(status='not_confirmed').count()

  def is_friends_with(self,user):
    friendship = self.friends().filter((Friendship.inviter_id==user.id)|(Friendship.invitee_id==user.id)).first()
    return friendship is not None and self != user

  def sent_friend_request_to(self,user):
    friend_request_sent = self.invitees.filter_by(status='not_confirmed').filter_by(invitee_id=user.id).first()
    return friend_request_sent is not None
  
  def received_friend_request_from(self,user):
    friend_request_received = self.inviters.filter_by(status='not_confirmed').filter_by(inviter_id=user.id).first()
    return friend_request_received is not None
  
  def can_send_friend_request_to(self,user):
    return not self.is_friends_with(user) and not self.sent_friend_request_to(user) and not self.received_friend_request_from(user)

  def send_friend_request_to(self,user):
    if self.can_send_friend_request_to(user):
      f = Friendship(inviter=self,invitee=user)
      db.session.add(f)
      db.session.commit()

  def accept_friend_request_from(self,user):
    if self.received_friend_request_from(user):
      f = self.inviters.filter_by(status='not_confirmed').filter_by(inviter_id=user.id).first()
      f.status = 'confirmed'
      db.session.commit()
  
  def decline_friend_request_from(self,user):
    if self.received_friend_request_from(user):
      f = self.inviters.filter_by(status='not_confirmed').filter_by(inviter_id=user.id).first()
      db.session.delete(f)
      db.session.commit()
  
  def remove_friend(self,user):
    if self.is_friends_with(user):
      friendship = self.friends().filter((Friendship.inviter_id==user.id)|(Friendship.invitee_id==user.id)).first()
      db.session.delete(friendship)
      db.session.commit()

  def new_questions(self):
    last_read_time = self.last_question_read_time or datetime(1900,1,1)
    return Question.query.filter_by(recipient=self).filter(Question.timestamp > last_read_time).count()
  
  # returns a list of new questions
  def new_questions_content(self):
    last_read_time = self.last_question_read_time or datetime(1900,1,1)
    return Question.query.filter_by(recipient=self).filter(Question.timestamp > last_read_time).all()
  
  # returns games awaiting user confirmation 
  def unconfirmed_games(self):
    return Game.query.filter_by(guest=self).filter(Game.status == 'not_confirmed').all()

  # returns games awaiting user answer
  def unanswered_games(self):
    return Game.query.filter(((Game.author == self) & (Game.turn == 'waiting_author_answer')) | ((Game.guest == self) & (Game.turn == 'waiting_guest_answer'))).all()

  # returns games awaiting user confirmation 
  def unconfirmed_games_count(self):
    return Game.query.filter_by(guest=self).filter(Game.status == 'not_confirmed').count()

  # returns games awaiting user answer
  def unanswered_games_count(self):
    return Game.query.filter(((Game.author == self) & (Game.turn == 'waiting_author_answer')) | ((Game.guest == self) & (Game.turn == 'waiting_guest_answer'))).count()

  # returns all games (whether user is author or guest)
  def all_games(self):
    return self.created_games.union(self.invited_games)

  def add_notifications(self,name,data):
    self.notifications.filter_by(name=name).delete()
    n = Notification(name=name, payload_json=json.dumps(data), user=self)
    db.session.add(n)
    db.session.commit()
    return n

  @property
  def password(self):
    raise AttributeError('password is not a readable attribute')
  
  @password.setter
  def password(self,password):
    self.password_hash = generate_password_hash(password)
  
  def verify_password(self,password):
    return check_password_hash(self.password_hash,password)

  def __init__(self,username,email,password):
    self.username = username
    self.email = email
    self.password = password 
  
  def __repr__(self):
    return f"<User {self.username}>"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)

class Drawing(db.Model):
  __tablename__ = 'drawings'
  id = db.Column(db.Integer,primary_key=True)
  filename = db.Column(db.String(64),unique=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  questions = db.relationship('Question',backref='drawing',cascade="all, delete-orphan",lazy='dynamic')
  timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
  display = db.Column(db.Boolean, default=False)

  def __init__(self,filename):
    self.filename = filename
  
  def __repr__(self):
    return f"<Drawing {self.filename}>"

class Question(db.Model):
  __tablename__ = 'questions'
  id = db.Column(db.Integer, primary_key=True)
  sender_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  drawing_id = db.Column(db.Integer, db.ForeignKey('drawings.id'))
  game_id = db.Column(db.Integer, db.ForeignKey('games.id'))
  answer = db.Column(db.String(64))
  timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
  max_tries = db.Column(db.Integer,default=3)
  num_of_tries = db.Column(db.Integer,default=0)
  status = db.Column(db.Enum('complete','in_progress','lost'),nullable=False,server_default="in_progress")
  hints = db.relationship('Hint',backref='question',lazy='dynamic',cascade="all, delete-orphan")

  def check_answer(self,answer):
    return self.answer == answer
  
  def check_lost(self):
    return self.max_tries == self.num_of_tries

  def __repr__(self):
    return f"<Question {self.answer}>"

class Hint(db.Model):
  __tablename__ = 'hints'
  id = db.Column(db.Integer, primary_key=True)
  body = db.Column(db.String(256))
  question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))

  def __repr__(self):
    return f"<Hint {self.body}>"

class Notification(db.Model):
  __tablename__ = 'notifications'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(128), index=True)
  user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  timestamp = db.Column(db.Float,index=True,default=time)
  payload_json = db.Column(db.Text)

  def get_data(self):
    return json.loads(str(self.payload_json))

class Game(db.Model):
  __tablename__ = 'games'
  id = db.Column(db.Integer, primary_key=True)
  author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  guest_id = db.Column(db.Integer, db.ForeignKey('users.id'))
  current_author_points = db.Column(db.Integer, default=0)
  current_guest_points = db.Column(db.Integer, default=0)
  max_points = db.Column(db.Integer)
  questions = db.relationship('Question',backref='game',lazy='dynamic',cascade="all, delete-orphan")
  timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

  # user is winner if status == 'user' and vice versa
  status = db.Column(db.Enum('not_confirmed','rejected','in_progress','author','guest'),nullable=False,server_default="not_confirmed")
  turn = db.Column(db.Enum('author','guest','waiting_author_answer','waiting_guest_answer'),nullable=False,server_default="author")

  def is_turn(self,user):
    if user is self.author and self.turn == 'author':
      return True
    
    if user is self.guest and self.turn == 'guest':
      return True
    
    return False
  
  # returns True if game is waiting for answer from user 
  def is_waiting_answer_from(self,user):
    if user is self.author and self.turn == 'waiting_author_answer':
      return True
    if user is self.guest and self.turn == 'waiting_guest_answer':
      return True
    
    return False

  # returns True if user is the author of game
  def is_author(self,user):
    return self.author is user
  
  # return True if author won game
  def is_author_win(self):
    return self.current_author_points >= self.max_points
  
  # return True if guest won game
  def is_guest_win(self):
    return self.current_guest_points >= self.max_points
  
  # returns True if user has won game
  def is_user_win(self,user):
    if self.is_author(user):
      return self.status == 'author'
    else:
      return self.status == 'guest'

  # returns True if user has won game
  def is_user_loss(self,user):
    if self.is_author(user):
      return self.status == 'guest'
    else:
      return self.status == 'author'

  # update the score of the user 
  def update_user_score(self,user,increment):
    if self.is_author(user):
      self.current_author_points = self.current_author_points + increment
    else:
      self.current_guest_points = self.current_guest_points + increment
  
  # make it the user's turn
  def make_user_turn(self,user):
    if self.is_author(user):
      self.turn = 'author'
    else:
      self.turn = 'guest'

  # validate that user1 and user2 are both players of the game
  def validate_players(self,user1,user2):
    return (user1 is self.author and user2 is self.guest) or (user1 is self.guest and user2 is self.author)
  
  # returns the user's opponent
  def get_opponent(self,user):
    if self.is_author(user):
      return self.guest
    else:
      return self.author

  def __repr__(self):
    return f"<Game {self.id}>"
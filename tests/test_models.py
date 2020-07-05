from base_cases import FlaskTestCase
from app.models import Drawing,Friendship,Game,Hint,Question,User
from app import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError
"""
class ModelRelationshipsTestCase(FlaskTestCase):
  def test_user_drawing(self):
    u1 = User(username='one',email='one@one.com',password='one')
    d1 = Drawing(filename='d1')
    d2 = Drawing(filename='d2')

    # before connecting
    self.assertEqual(u1.drawings.count(),0)
    self.assertFalse(d1 in u1.drawings.all())
    self.assertFalse(d2 in u1.drawings.all())

    d1.user = u1
    d2.user = u1
    self.assertEqual(u1.drawings.count(),2)
    self.assertTrue(d1 in u1.drawings.all())
    self.assertTrue(d2 in u1.drawings.all())

  def test_drawing_question(self):
    d1 = Drawing(filename='d1')
    q1 = Question(answer='q1')
    q2 = Question(answer='q2')

    # before connecting
    self.assertEqual(len(d1.questions.all()),0)
    self.assertFalse(q1 in d1.questions.all())
    self.assertFalse(q2 in d1.questions.all())

    q1.drawing = d1
    q2.drawing = d1
    self.assertEqual(len(d1.questions.all()),2)
    self.assertTrue(q1 in d1.questions.all())
    self.assertTrue(q2 in d1.questions.all())

  def test_user_question(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')

    q1 = Question(answer='q1',author=u1,recipient=u2)
    q2 = Question(answer='q2',author=u2,recipient=u1)

    db.session.add_all([u1,u2,q1,q2])

    self.assertTrue(q1 in u1.questions_sent.all())
    self.assertFalse(q2 in u1.questions_sent.all())
    self.assertTrue(q2 in u2.questions_sent.all())
    self.assertFalse(q1 in u2.questions_sent.all())
    self.assertFalse(q1 in u1.questions_received.all())
    self.assertTrue(q2 in u1.questions_received.all())
    self.assertFalse(q2 in u2.questions_received.all())
    self.assertTrue(q1 in u2.questions_received.all())
  
  def test_question_game(self):
    g1 = Game()
    q1 = Question(answer='q1')
    q2 = Question(answer='q2')

    # before connecting
    self.assertEqual(g1.questions.count(),0)

    # after connecting
    q1.game = g1
    q2.game = g1
    self.assertEqual(g1.questions.count(),2)
    self.assertTrue(q1 in g1.questions.all())
    self.assertTrue(q2 in g1.questions.all())

  def test_hint_question(self):
    q1 = Question(answer='q1')
    h1 = Hint(body='h1')
    h2 = Hint(body='h2')

    # before connecting
    self.assertEqual(q1.hints.count(),0)

    # after connecting
    h1.question = q1
    h2.question = q1
    self.assertEqual(q1.hints.count(),2)
    self.assertTrue(h1 in q1.hints.all())
    self.assertTrue(h2 in q1.hints.all())
  
  def test_user_game(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    g1 = Game(author=u1,guest=u2)
    g2 = Game(author=u2,guest=u1)
    
    self.assertEqual(u1.created_games.count(),1)
    self.assertEqual(u1.invited_games.count(),1)
    self.assertEqual(u2.created_games.count(),1)
    self.assertEqual(u2.invited_games.count(),1)

    self.assertTrue(g1 in u1.created_games.all())
    self.assertTrue(g2 in u1.invited_games.all())
    self.assertTrue(g1 in u2.invited_games.all())
    self.assertTrue(g2 in u2.created_games.all())

  def test_cascades(self):
    # If User deleted, Drawing deleted
    u1 = User(username='one',email='one@one.com',password='one')
    d1 = Drawing(filename='d1')
    d1.user = u1
    db.session.add_all([u1,d1])
    db.session.commit()
    self.assertEqual(Drawing.query.count(),1)
    db.session.delete(u1)
    db.session.commit()
    self.assertEqual(Drawing.query.count(),0)

    # If User deleted, Question deleted
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    q1 = Question(answer='q1')
    q2 = Question(answer='q2')
    q1.author = u1
    q1.recipient = u2
    q2.author = u2
    q2.recipient = u1
    db.session.add_all([u1,u2,q1,q2])
    db.session.commit()
    self.assertEqual(Question.query.count(),2)
    db.session.delete(u1)
    db.session.delete(u2)
    db.session.commit()
    self.assertEqual(Question.query.count(),0)

    # If User deleted, Game deleted
    u1 = User(username='one',email='one@one.com',password='one')
    g1 = Game(author=u1)
    g2 = Game(guest=u1)
    db.session.add_all([u1,g1,g2])
    db.session.commit()
    self.assertEqual(Game.query.count(),2)
    db.session.delete(u1)
    db.session.commit()
    self.assertEqual(Game.query.count(),0)

    # If User deleted, Friendship Deleted
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    f1 = Friendship(inviter=u1,invitee=u2)
    f2 = Friendship(inviter=u2,invitee=u1)
    db.session.add_all([u1,u2,f1,f2])
    db.session.commit()
    self.assertEqual(Friendship.query.count(),2)
    db.session.delete(u1)
    db.session.delete(u2)
    db.session.commit()
    self.assertEqual(Friendship.query.count(),0)

    # If Drawing deleted, Question deleted
    d1 = Drawing(filename='d1')
    q1 = Question(answer='q1')
    q1.drawing = d1
    db.session.add_all([d1,q1])
    db.session.commit()
    self.assertEqual(Question.query.count(),1)
    db.session.delete(d1)
    db.session.commit()
    self.assertEqual(Question.query.count(),0)

    # If Question deleted, Hint deleted
    q1 = Question(answer='q1')
    h1 = Hint(body='h1')
    h1.question = q1
    db.session.add_all([h1,q1])
    db.session.commit()
    self.assertEqual(Hint.query.count(),1)
    db.session.delete(q1)
    db.session.commit()
    self.assertEqual(Hint.query.count(),0)

    # If Game deleted, Question deleted
    g1 = Game()
    q1 = Question(answer='q1')
    q1.game = g1
    db.session.add_all([g1,q1])
    db.session.commit()
    self.assertEqual(Question.query.count(),1)
    db.session.delete(g1)
    db.session.commit()
    self.assertEqual(Question.query.count(),0)

class FriendshipModelTestCase(FlaskTestCase):
  def test_tablename(self):
    self.assertEqual(Friendship.__tablename__,'friendships')
  
  def test_attributes(self):
    user1 = User(username='one',email='one@one.com',password='one')
    user2 = User(username='two',email='two@two.com',password='two')
    before = datetime.utcnow()
    f = Friendship(inviter=user1,invitee=user2)
    db.session.add_all([user1,user2,f])
    db.session.commit()
    after = datetime.utcnow()

    self.assertEqual(f.status,'not_confirmed')
    self.assertEqual(f.inviter_id,1)
    self.assertEqual(f.invitee_id,2)
    self.assertTrue(f.timestamp > before and f.timestamp < after)
    self.assertEqual(f.inviter_games_won,0)
    self.assertEqual(f.invitee_games_won,0)

  def test_get_friend(self):
    user1 = User(username='one',email='one@one.com',password='one')
    user2 = User(username='two',email='two@two.com',password='two')
    f = Friendship(inviter=user1,invitee=user2)
    db.session.add_all([user1,user2,f])
    db.session.commit()

    self.assertEqual(f.get_friend(user1),user2)
    self.assertEqual(f.get_friend(user2),user1)

class UserModelTestCase(FlaskTestCase):
  def test_password_setter(self):
    u = User(username='one',email='one@one.com',password='one')
    self.assertTrue(u.password_hash is not None)
  
  def test_no_password_getter(self):
    u = User(username='one',email='one@one.com',password='one')
    with self.assertRaises(AttributeError):
      u.password
  
  def test_password_verification(self):
    u = User(username='one',email='one@one.com',password='one')
    self.assertTrue(u.verify_password('one'))
    self.assertFalse(u.verify_password('two'))
  
  def test_password_salts_are_random(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='one',email='one@one.com',password='one')
    self.assertTrue(u1.password_hash != u2.password_hash)

  def test_attributes(self):
    before = datetime.utcnow()
    u1 = User(email='test@test.com',username='test',password='test')
    u1.last_question_read_time = datetime.utcnow()
    db.session.add(u1)
    db.session.commit()
    after = datetime.utcnow()

    self.assertEqual(u1.email,'test@test.com')
    self.assertEqual(u1.username,'test')
    self.assertEqual(u1.id,1)
    self.assertEqual(u1.__repr__(),'<User test>')
    self.assertEqual(u1.__tablename__, 'users')
    self.assertTrue(u1.last_question_read_time > before and u1.last_question_read_time < after)

  
  def test_non_unique_email(self):
    u1 = User(email='one@one.com', username='one', password='one')
    u2 = User(email='one@one.com',username='two',password='two')

    db.session.add(u1)
    db.session.commit()

    with self.assertRaises(IntegrityError):
      db.session.add(u2)
      db.session.commit()

  def test_non_unique_username(self):
    u1 = User(email='one@one.com', username='one', password='one')
    u2 = User(email='two@two.com',username='one',password='two')

    db.session.add(u1)
    db.session.commit()

    with self.assertRaises(IntegrityError):
      db.session.add(u2)
      db.session.commit()
  
  def test_user_questions_methods(self):
    u1 = User(email='one@one.com', username='one', password='one')
    db.session.add(u1)
    db.session.commit()
    
    # new_questions() and new_questions_content()
    q1 = Question(answer='q1')
    q1.recipient = u1
    db.session.add(q1)
    db.session.commit()
    u1.last_question_read_time = datetime.utcnow()
    db.session.commit()
    self.assertEqual(u1.new_questions(),0)
    self.assertFalse(q1 in u1.new_questions_content())

    q2 = Question(answer='q2')
    q2.recipient = u1
    db.session.add(q2)
    db.session.commit()
    self.assertEqual(u1.new_questions(),1)
    self.assertTrue(q2 in u1.new_questions_content())

  def test_user_games_methods(self):
    u1 = User(email='one@one.com', username='one', password='one')
    u2 = User(email='two@two.com', username='two', password='two')
    db.session.add(u1)
    db.session.add(u2)
    db.session.commit()

    # unconfirmed_games() and unconfirmed_games_count()
    self.assertEqual(u1.unconfirmed_games_count(),0)
    game1 = Game(guest=u1,max_points=7)
    db.session.add(game1)
    db.session.commit()
    self.assertEqual(u1.unconfirmed_games_count(),1)
    self.assertTrue(game1 in u1.unconfirmed_games())

    game2 = Game(author=u2,guest=u1,status='waiting_guest_answer',max_points=7)
    game3 = Game(author=u1,guest=u2,status='waiting_author_answer',max_points=7)
    game4 = Game(author=u2,guest=u1,status='waiting_author_answer',max_points=7)
    game5 = Game(author=u1,guest=u2,status='waiting_guest_answer',max_points=7)
    db.session.add_all([game2,game3,game4,game5])
    db.session.commit()

    # test all games  
    self.assertEqual(u1.all_games().count(),5)

    # test in_progress_games() and completed_games()
    self.assertEqual(u1.completed_games().count(),0)
    self.assertEqual(u1.in_progress_games().count(),4)
    game3.status = 'author_win'
    db.session.commit()
    self.assertEqual(u1.in_progress_games().count(),3)
    self.assertEqual(u1.completed_games().count(),1)

  def test_friendship_functionality(self):
    u1 = User(email='one@one.com', username='one', password='one')
    u2 = User(email='two@two.com',username='two',password='two')
    db.session.add_all([u1,u2])
    db.session.commit()

    # before being friends
    self.assertEqual(len(u1.invitees.all()),0)
    self.assertEqual(len(u1.inviters.all()),0)
    self.assertEqual(len(u1.friends().all()),0)
    self.assertEqual(len(u2.invitees.all()),0)
    self.assertEqual(len(u2.inviters.all()),0)
    self.assertEqual(len(u2.friends().all()),0)
    self.assertFalse(u1.is_friends_with(u2))
    self.assertEqual(len(u2.pending_friend_requests().all()),0)
    self.assertEqual(u2.pending_friend_requests_count(),0)
    self.assertFalse(u1.sent_friend_request_to(u2))
    self.assertTrue(u1.can_send_friend_request_to(u2))

    # after friend request sent (from u1 to u2)
    u1.send_friend_request_to(u2)
    self.assertEqual(len(u1.invitees.all()),1)
    self.assertEqual(len(u2.inviters.all()),1)
    self.assertEqual(len(u2.pending_friend_requests().all()),1)
    self.assertEqual(u2.pending_friend_requests_count(),1)
    self.assertTrue(u1.sent_friend_request_to(u2))
    self.assertFalse(u1.can_send_friend_request_to(u2))

    # after friend request accepted (by u2)
    u2.accept_friend_request_from(u1)
    self.assertTrue(u1.is_friends_with(u2))
    self.assertEqual(len(u1.invitees.all()),1)
    self.assertEqual(len(u1.inviters.all()),0)
    self.assertEqual(len(u1.friends().all()),1)
    self.assertEqual(len(u2.invitees.all()),0)
    self.assertEqual(len(u2.inviters.all()),1)
    self.assertEqual(len(u2.friends().all()),1)
    self.assertEqual(len(u2.pending_friend_requests().all()),0)
    self.assertEqual(u2.pending_friend_requests_count(),0)
    self.assertFalse(u1.sent_friend_request_to(u2))
    self.assertFalse(u1.can_send_friend_request_to(u2))

    # after remove friend
    u1.remove_friend(u2)
    self.assertFalse(u1.is_friends_with(u2))
    self.assertEqual(len(u1.invitees.all()),0)
    self.assertEqual(len(u1.inviters.all()),0)
    self.assertEqual(len(u1.friends().all()),0)
    self.assertEqual(len(u2.invitees.all()),0)
    self.assertEqual(len(u2.inviters.all()),0)
    self.assertEqual(len(u2.friends().all()),0)
    self.assertEqual(len(u2.pending_friend_requests().all()),0)
    self.assertEqual(u2.pending_friend_requests_count(),0)
    self.assertFalse(u1.sent_friend_request_to(u2))
    self.assertTrue(u1.can_send_friend_request_to(u2))

    # test friend acceptance decline
    u2.send_friend_request_to(u1)
    self.assertEqual(len(u1.invitees.all()),0)
    self.assertEqual(len(u1.inviters.all()),1)
    self.assertEqual(len(u1.friends().all()),0)
    self.assertEqual(len(u2.invitees.all()),1)
    self.assertEqual(len(u2.inviters.all()),0)
    self.assertEqual(len(u2.friends().all()),0)
    self.assertFalse(u1.is_friends_with(u2))
    self.assertEqual(len(u1.pending_friend_requests().all()),1)
    self.assertEqual(u1.pending_friend_requests_count(),1)
    self.assertTrue(u2.sent_friend_request_to(u1))
    self.assertFalse(u2.can_send_friend_request_to(u1))
    u1.decline_friend_request_from(u2)
    self.assertEqual(len(u1.invitees.all()),0)
    self.assertEqual(len(u1.inviters.all()),0)
    self.assertEqual(len(u1.friends().all()),0)
    self.assertEqual(len(u2.invitees.all()),0)
    self.assertEqual(len(u2.inviters.all()),0)
    self.assertEqual(len(u2.friends().all()),0)
    self.assertFalse(u1.is_friends_with(u2))
    self.assertEqual(len(u1.pending_friend_requests().all()),0)
    self.assertEqual(u1.pending_friend_requests_count(),0)
    self.assertFalse(u2.sent_friend_request_to(u1))
    self.assertTrue(u2.can_send_friend_request_to(u1))
"""
class GameModelTestCase(FlaskTestCase):
  def test_tablename(self):
    self.assertEqual(Game.__tablename__,'games')
  
  def test_attributes(self):
    before = datetime.utcnow()
    game = Game(
      current_author_points=7,
      current_guest_points=8,
      max_points=8
    )
    db.session.add(game)
    db.session.commit()
    after = datetime.utcnow()

    self.assertEqual(game.id,1)
    self.assertEqual(game.current_author_points,7)
    self.assertEqual(game.current_guest_points,8)
    self.assertEqual(game.max_points,8)
    self.assertTrue(before < game.timestamp and game.timestamp < after)
    self.assertEqual(game.status,'not_confirmed')

  def test_methods(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    game = Game(
      current_author_points=7,
      current_guest_points=8,
      max_points=8,
      author=u1,
      guest=u2,
      status='guest_win'
    )
    db.session.add_all([u1,u2,game])
    db.session.commit()
    # checking wins
    self.assertFalse(game.is_user_win(u1))
    self.assertTrue(game.is_user_loss(u1))
    self.assertTrue(game.is_user_win(u2))
    self.assertFalse(game.is_user_loss(u2))

    # turn-related methods
    self.assertFalse(game.is_in_progress())
    game.status = 'author_turn_to_ask'
    db.session.commit()
    self.assertTrue(game.is_in_progress())
    self.assertTrue(game.is_turn(u1))
    self.assertFalse(game.is_turn(u2))
    game.status = 'waiting_author_answer'
    db.session.commit()
    self.assertTrue(game.is_waiting_answer_from(u1))
    self.assertFalse(game.is_waiting_answer_from(u2))

    # update score 
    game.update_user_score(u1,10)
    self.assertEqual(game.current_author_points,17)

    # user validation methods
    self.assertTrue(game.is_author(u1))
    self.assertFalse(game.is_author(u2))

    u3 = User(username='three',email='three@three.com',password='three')
    self.assertTrue(game.validate_players(u1,u2))
    self.assertFalse(game.validate_players(u1,u3))

    self.assertEqual(game.get_opponent(u1),u2)
    self.assertEqual(game.get_opponent(u2),u1)

    # win update
    game2 = Game(
      current_author_points=7,
      current_guest_points=8,
      max_points=8,
      author=u1,
      guest=u2,
      status='author_turn_to_ask'
    )
    game2.win_update()
    self.assertTrue(game2.status == 'guest_win')

    # turn_update
    game3 = Game(
      current_author_points=7,
      current_guest_points=8,
      max_points=8,
      author=u1,
      guest=u2,
      status='author_turn_to_ask'
    )
    self.assertEqual(game3.status,'author_turn_to_ask')
    game3.turn_update()
    self.assertEqual(game3.status,'waiting_guest_answer')
    game3.turn_update()
    self.assertEqual(game3.status,'guest_turn_to_ask')
    game3.turn_update()
    self.assertEqual(game3.status,'waiting_author_answer')
    game3.turn_update()
    self.assertEqual(game3.status,'author_turn_to_ask')

    # accept game
    game4 = Game(
      current_author_points=7,
      current_guest_points=8,
      max_points=8,
      author=u1,
      guest=u2,
      status='not_confirmed'
    )
    game4.accept_game()
    self.assertTrue(game4.status=='author_turn_to_ask' or game4.status=='guest_turn_to_ask')

  def test_repr(self):
    game = Game()
    db.session.add(game)
    db.session.commit()
    self.assertEqual(game.__repr__(),'<Game 1>')

class HintModelTestCase(FlaskTestCase):
  def test_tablename(self):
    self.assertEqual(Hint.__tablename__,'hints')

  def test_attributes(self):
    hint = Hint(body='hint1')
    db.session.add(hint)
    db.session.commit()

    self.assertEqual(hint.id,1)
    self.assertEqual(hint.body,'hint1')

  def test_repr(self):
    hint = Hint(body='hint1')
    self.assertEqual(hint.__repr__(),'<Hint hint1>')

class QuestionModelTestCase(FlaskTestCase):
  def test_tablename(self):
    self.assertEqual(Question.__tablename__,'questions')

  def test_attributes(self):
    before = datetime.utcnow()
    question = Question(answer='question1')
    question.max_tries = 7
    db.session.add(question)
    db.session.commit()
    after = datetime.utcnow()

    self.assertEqual(question.id,1)
    self.assertEqual(question.answer,'question1')
    self.assertTrue(question.timestamp > before and question.timestamp < after)
    self.assertEqual(question.max_tries,7)
    self.assertEqual(question.num_of_tries,0)
    self.assertEqual(question.status,'in_progress')

  def test_check_answer(self):
    question = Question(answer='question1')
    self.assertTrue(question.check_answer('question1'))
    self.assertFalse(question.check_answer('notquestion1'))
  
  def test_check_lost(self):
    question = Question(answer='question1')
    question.max_tries = 7
    question.num_of_tries = 0
    self.assertFalse(question.check_lost())
    question.num_of_tries=7
    self.assertTrue(question.check_lost())

  def test_repr(self):
    question = Question(answer='question1')
    self.assertEqual(question.__repr__(),'<Question question1>')

class DrawingModelTestCase(FlaskTestCase):
  def test_tablename(self):
    self.assertEqual(Drawing.__tablename__,'drawings')
  
  def test_attributes(self):
    before = datetime.utcnow()
    drawing = Drawing(filename='drawing1')
    db.session.add_all([drawing])
    db.session.commit()
    after = datetime.utcnow() 

    # test attributes
    self.assertEqual(drawing.id,1)
    self.assertEqual(drawing.filename,'drawing1')
    self.assertTrue(drawing.timestamp > before and drawing.timestamp < after)
    self.assertEqual(drawing.display,False)
    
  
  def test_repr(self):
    drawing = Drawing(filename='filename')
    self.assertEqual(drawing.__repr__(), '<Drawing filename>')
    
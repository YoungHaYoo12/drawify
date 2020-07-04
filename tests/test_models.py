from base_cases import FlaskTestCase
from app.models import Drawing,Friendship,Game,Hint,Question,User
from app import db
from datetime import datetime
from sqlalchemy.exc import IntegrityError

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

    # unanswered_games() and unanswered_games_count()
    self.assertEqual(u1.unanswered_games_count(),0)
    game2 = Game(author=u2,guest=u1,turn='waiting_guest_answer',max_points=7)
    game3 = Game(author=u1,guest=u2,turn='waiting_author_answer',max_points=7)
    game4 = Game(author=u2,guest=u1,turn='waiting_author_answer',max_points=7)
    game5 = Game(author=u1,guest=u2,turn='waiting_guest_answer',max_points=7)
    db.session.add_all([game2,game3,game4,game5])
    db.session.commit()
    self.assertEqual(u1.unanswered_games_count(),2)
    self.assertTrue(game2 in u1.unanswered_games())
    self.assertTrue(game3 in u1.unanswered_games())
    self.assertFalse(game4 in u1.unanswered_games())
    self.assertFalse(game5 in u1.unanswered_games())

    # test all games 
    self.assertEqual(u1.all_games().count(),5)

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
    self.assertEqual(game.turn,'author')

  def test_methods(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    game = Game(
      current_author_points=7,
      current_guest_points=8,
      max_points=8,
      author=u1,
      guest=u2,
      turn='author'
    )
    # checking wins
    self.assertFalse(game.is_author_win())
    self.assertTrue(game.is_guest_win())
    self.assertFalse(game.is_user_win(u1))
    self.assertTrue(game.is_user_loss(u1))
    self.assertTrue(game.is_user_win(u2))
    self.assertFalse(game.is_user_loss(u2))

    # turn-related methods
    self.assertTrue(game.is_turn(u1))
    self.assertFalse(game.is_turn(u2))
    game.make_user_turn(u2)
    self.assertFalse(game.is_turn(u1))
    self.assertTrue(game.is_turn(u2))
    game.turn = 'waiting_author_answer'
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
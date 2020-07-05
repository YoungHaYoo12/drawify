from base_cases import FlaskClientTestCase
from flask import url_for
from app.models import Drawing,Game,Hint,User,Question
from app import db
from datetime import datetime

class FlaskQuestionsTestCase(FlaskClientTestCase):
  def test_question(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    q1 = Question(answer='q1')
    q2 = Question(answer='q2')
    q3 = Question(answer='q3')
    g1 = Game(author=u1,guest=u2,max_points=2,status='waiting_author_answer')
    d1 = Drawing(filename='d1')
    q1.drawing = d1
    q1.author = u2
    q1.recipient = u1
    q1.game = g1
    q1.max_tries=2
    q3.drawing = d1 
    q3.author = u2
    q3.recipient = u1
    q3.game = g1
    q3.max_tries=2
    q3.status='lost'
    db.session.add_all([u1,u2,q1,q2,q3,g1])
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'),data={
        'email':'one@one.com',
        'password':'one'
      })

      # invalid question 
      response = self.client.get(url_for('questions.question',id=100))
      self.assertEqual(response.status_code,404)

      # question does not belong to user 
      response = self.client.get(url_for('questions.question',id=q2.id))
      self.assertEqual(response.status_code,403)

      # question not in progress
      self.assertEqual(q3.num_of_tries,0)
      response = self.client.get(url_for('questions.question',id=q3.id))
      self.assertEqual(q3.num_of_tries,0)

      # if question answered incorrectly (but no loss or win)
      response = self.client.post(url_for('questions.question',id=q1.id),data={
        'answer':'incorrect'
      },follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('Incorrect. Please Try Again.' in data)
      self.assertEqual(q1.num_of_tries,1)

      # if user runs out of tries on question
      response = self.client.post(url_for('questions.question',id=q1.id),data={
        'answer':'incorrect'
      },follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('Incorrect. You Have Run Out of Tries On This Question' in data)
      self.assertEqual(q1.num_of_tries,2)
      self.assertEqual(q1.status,'lost')
      # check that game was updated correctly
      self.assertEqual(g1.status,'author_turn_to_ask')

      # if user answers question correctly
      g1.status = 'waiting_author_answer'
      q1.status = 'in_progress'
      q1.num_of_tries = 1
      db.session.commit()
      response = self.client.post(url_for('questions.question',id=q1.id),data={
        'answer':'q1'
      },follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('Question Answered Correctly' in data)
      self.assertEqual(q1.num_of_tries,2)
      self.assertEqual(q1.status,'complete')
      # check that game was updated correctly
      self.assertEqual(g1.status,'author_turn_to_ask')

      # if user answers question correctly (leading to game win)
      g1.status = 'waiting_author_answer'
      q1.status = 'in_progress'
      q1.num_of_tries = 1
      db.session.commit()
      response = self.client.post(url_for('questions.question',id=q1.id),data={
        'answer':'q1'
      },follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('Question Answered Correctly' in data)
      self.assertEqual(q1.num_of_tries,2)
      self.assertEqual(q1.status,'complete')
      # check that game was updated correctly
      self.assertEqual(g1.status,'author_win')

  def test_list(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    u3 = User(username='three',email='three@three.com',password='three')
    q1 = Question(answer='q1')
    q2 = Question(answer='q2')
    g1 = Game()
    q1.author = u2
    q2.author = u3
    q1.recipient = u1
    q2.recipient = u1
    q1.game = g1
    q2.game = g1

    db.session.add_all([u1,u2,u3,q1,q2,g1])
    db.session.commit()
    u1.last_question_read_time = datetime.utcnow()
    q2.timestamp = datetime.utcnow()
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'),data={
        'email':'one@one.com',
        'password':'one'
      })

      # test that only q2 appears (since q1.timestamp  < u1.last_question_read_time)
      response = self.client.get(url_for('questions.list'))
      data = response.get_data(as_text=True)
      self.assertTrue('Game Against three' in data)
      self.assertFalse('Game Against two' in data)

  def test_send_hint(self):
    u1 = User(username='one',email='one@one.com',password='one')
    q1 = Question(answer='q1')
    q2 = Question(answer='q2')
    d1 = Drawing(filename='d1')
    q1.drawing = d1
    q1.author = u1
    db.session.add_all([q1,q2,u1,d1])
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'),data={
        'email':'one@one.com',
        'password':'one'
      })
      # invalid question 
      response = self.client.get(url_for('questions.send_hint',question_id=100))
      self.assertEqual(response.status_code,404)

      # question does not belong to user 
      response = self.client.get(url_for('questions.send_hint',question_id=q2.id))
      self.assertEqual(response.status_code,403)

      # successful post 
      response = self.client.post(url_for('questions.send_hint',question_id=q1.id),data={
        'body':'hint1'
      },follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('Hint Successfully Submitted' in data)
      hint1 = Hint.query.get(1)
      self.assertEqual(hint1.body,'hint1')
      self.assertEqual(hint1.question,q1)

  def test_send_question(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    d1 = Drawing(filename='d1')
    g1 = Game(author=u1,guest=u2,max_points=1)
    d1.user = u1
    db.session.add_all([u1,u2,d1,g1])
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'),data={
        'email':'one@one.com',
        'password':'one'
      })

      # if not current user's turn 
      g1.status = 'guest_turn_to_ask'
      db.session.commit()
      response = self.client.get(url_for('questions.send_question',recipient='two',game_id=g1.id,drawing_id=d1.id),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('It is currently not your turn.' in data)

      # successful post 
      g1.status = 'author_turn_to_ask'
      response = self.client.post(url_for('questions.send_question',recipient='two',drawing_id=d1.id,game_id=g1.id),data={
        'answer':'questionjustadded',
        'max_tries':10
      },follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('Your question has been sent.' in data)
      # test that question has been created
      q1 = Question.query.get(1)
      self.assertEqual(q1.author,u1)
      self.assertEqual(q1.recipient,u2)
      self.assertEqual(q1.max_tries,10)
      self.assertEqual(q1.answer,'questionjustadded')
      # test that game status has been updated
      self.assertEqual(g1.status,'waiting_guest_answer')


  def test_choose_send_question_and_send_question_validators(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    u3 = User(username='three',email='three@three.com',password='three')
    d1 = Drawing(filename='d1')
    d2 = Drawing(filename='d2')
    g1 = Game(author=u1,guest=u2,max_points=1)
    d1.user = u1
    db.session.add_all([u1,u2,u3,d1,d2,g1])
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'),data={
        'email':'one@one.com',
        'password':'one'
      })
      # invalid user 
      response = self.client.get(url_for('questions.choose_send_question',recipient='notvalid',game_id=g1.id))
      self.assertEqual(response.status_code,404)
      response = self.client.get(url_for('questions.send_question',recipient='notvalid',game_id=g1.id,drawing_id=d1.id))
      self.assertEqual(response.status_code,404)

      # invalid game 
      response = self.client.get(url_for('questions.choose_send_question',recipient='two',game_id=100))
      self.assertEqual(response.status_code,404)
      response = self.client.get(url_for('questions.send_question',recipient='two',game_id=100,drawing_id=d1.id))
      self.assertEqual(response.status_code,404)

      # invalid Drawing
      response = self.client.get(url_for('questions.send_question',recipient='two',game_id=g1.id,drawing_id=100))
      self.assertEqual(response.status_code,404)
      response = self.client.get(url_for('questions.send_question',recipient='two',game_id=g1.id,drawing_id=d2.id))
      self.assertEqual(response.status_code,403)

      # users not validated by game 
      response = self.client.get(url_for('questions.choose_send_question',recipient='three',game_id=g1.id))
      self.assertEqual(response.status_code,403)
      response = self.client.get(url_for('questions.choose_send_question',recipient='three',game_id=g1.id,drawing_id=d1.id))
      self.assertEqual(response.status_code,403)

      # successful Connection
      response = self.client.get(url_for('questions.choose_send_question',recipient='two',game_id=g1.id))
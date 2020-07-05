from base_cases import FlaskClientTestCase
from flask import url_for
from flask_login import current_user
from app.models import Drawing,Game,Question,User
from app import db

class FlaskGamesTestCase(FlaskClientTestCase):
  def test_reject_invite(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    u3 = User(username='three',email='three@three.com',password='three')
    g1 = Game(author=u2,guest=u1,status='not_confirmed')
    g2 = Game(author=u2,guest=u1,status='author_win')
    g3 = Game(author=u3,guest=u2,status='not_confirmed')
    db.session.add_all([u1,u2,u3,g1,g2,g3])
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )
      # invalid game
      response = self.client.get(url_for('games.reject_invite',game_id=100))
      self.assertEqual(response.status_code,404)

      # user not game guest
      response = self.client.get(url_for('games.reject_invite',game_id=g3.id),follow_redirects=True)
      self.assertEqual(response.status_code,403)

      # game status is not 'not_confirmed'
      response = self.client.get(url_for('games.reject_invite',game_id=g2.id),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('The current game is not awaiting confirmation.' in data)
      self.assertEqual(g2.status,'author_win')

      # success 
      self.assertEqual(g1.status,'not_confirmed')
      response = self.client.get(url_for('games.reject_invite',game_id=g1.id),follow_redirects=True)
      self.assertEqual(g1.status,'rejected')

  def test_accept_invite(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    u3 = User(username='three',email='three@three.com',password='three')
    g1 = Game(author=u2,guest=u1,status='not_confirmed')
    g2 = Game(author=u2,guest=u1,status='author_win')
    g3 = Game(author=u3,guest=u2,status='not_confirmed')
    db.session.add_all([u1,u2,u3,g1,g2,g3])
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )
      # invalid game
      response = self.client.get(url_for('games.accept_invite',game_id=100))
      self.assertEqual(response.status_code,404)

      # user not game guest
      response = self.client.get(url_for('games.accept_invite',game_id=g3.id),follow_redirects=True)
      self.assertEqual(response.status_code,403)

      # game status is not 'not_confirmed'
      response = self.client.get(url_for('games.accept_invite',game_id=g2.id),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('The current game is not awaiting confirmation.' in data)
      self.assertEqual(g2.status,'author_win')

      # success
      self.assertEqual(g1.status,'not_confirmed')
      response = self.client.get(url_for('games.accept_invite',game_id=g1.id),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertNotEqual(g1.status,'not_confirmed')

  def test_send_invite(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    u3 = User(username='three',email='three@three.com',password='three')
    db.session.add_all([u1,u2,u3])
    db.session.commit()
    u1.send_friend_request_to(u2)
    u2.accept_friend_request_from(u1)
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )
      # invalid user
      response = self.client.get(url_for('games.send_invite',opponent_username='wowowo'))
      self.assertEqual(response.status_code,404)

      # user who is not a friend
      response = self.client.get(url_for('games.send_invite',opponent_username='three'),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('You cannot challenge users who are not your friends.' in data)
      self.assertEqual(Game.query.count(),0)

      # successful post 
      response = self.client.post(url_for('games.send_invite',opponent_username='two'),data={
        'author':current_user,
        'guest':u2,
        'max_points':10
      },follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('Game Invitation Sent' in data)
      game = Game.query.get(1)
      self.assertEqual(game.author,u1)
      self.assertEqual(game.guest,u2)
      self.assertEqual(game.max_points,10)


  def test_pending_games(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    u3 = User(username='three',email='three@three.com',password='three')
    g1 = Game(author=u1,guest=u2,max_points=1,status='not_confirmed')
    g2 = Game(author=u2,guest=u1,max_points=1,status='not_confirmed')
    g3 = Game(author=u3,guest=u1,max_points=1,status='author_win')
    db.session.add_all([u1,u2,u3,g1,g2,g3])
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )

      response = self.client.get(url_for('games.pending_games'))
      data = response.get_data(as_text=True)
      self.assertTrue('Game Invitation From two' in data)
      self.assertFalse('Game Invitation From one' in data)
      self.assertFalse('Game Invitation From three' in data)

  def test_list(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    u3 = User(username='three',email='three@three.com',password='three')
    u4 = User(username='four',email='four@four.com',password='four')

    g1 = Game(author=u1,guest=u2,max_points=1,status='author_win')
    g2 = Game(author=u1,guest=u3,max_points=1,status='author_turn_to_ask')
    g3 = Game(author=u4,guest=u1,max_points=1,status='not_confirmed')

    db.session.add_all([u1,u2,u3,u4,g1,g2,g3])
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )

      response = self.client.get(url_for('games.list'))
      data = response.get_data(as_text=True)
      self.assertEqual(response.status_code,200)
      self.assertTrue('one VS. two' in data)
      self.assertTrue('one VS. three' in data)
      self.assertTrue('four VS. one' in data)

  def test_game(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    u3 = User(username='three',email='three@three.com',password='three')
    u4 = User(username='four',email='four@four.com',password='four')

    g1 = Game(author=u3,guest=u4,max_points=2)
    g2 = Game(author=u1,guest=u2,max_points=10)
    q1 = Question(answer='q1')
    q1.game = g2

    db.session.add_all([u1,u2,u3,u4,g1,g2,q1])
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )

      # invalid game 
      response = self.client.get(url_for('games.game',game_id=100))
      self.assertEqual(response.status_code,404)

      # game not belonging to user 
      response = self.client.get(url_for('games.game',game_id=g1.id))
      self.assertEqual(response.status_code,403)

      # test valid game page
      # game status
      response = self.client.get(url_for('games.game',game_id=g2.id))
      data = response.get_data(as_text=True)
      self.assertTrue('Waiting for Game Confirmation' in data)

      g2.status = 'author_turn_to_ask'
      g2.turn='author'
      db.session.commit()
      response = self.client.get(url_for('games.game',game_id=g2.id))
      data = response.get_data(as_text=True)           
      self.assertTrue('Ask Your Opponent A Question!' in data)

      g2.status = 'rejected'
      db.session.commit()
      response = self.client.get(url_for('games.game',game_id=g2.id))
      data = response.get_data(as_text=True)      
      self.assertTrue('Game Has Been Rejected.' in data)

      g2.status = 'not_confirmed'
      db.session.commit()
      response = self.client.get(url_for('games.game',game_id=g2.id))
      data = response.get_data(as_text=True)      
      self.assertTrue('Waiting for Game Confirmation' in data)

      g2.status = 'author_win'
      db.session.commit()
      response = self.client.get(url_for('games.game',game_id=g2.id))
      data = response.get_data(as_text=True)      
      self.assertTrue('Congratulations, You Have Won!' in data)
      self.assertFalse('Send Question' in data)

      g2.status = 'guest_win'
      db.session.commit()
      response = self.client.get(url_for('games.game',game_id=g2.id))
      data = response.get_data(as_text=True)      
      self.assertTrue('You Have Lost.' in data)

      g2.status = 'waiting_author_answer'
      db.session.commit()
      response = self.client.get(url_for('games.game',game_id=g2.id))
      data = response.get_data(as_text=True)      
      self.assertTrue("Answer Your Opponent's Question!" in data)

      g2.status = 'guest_turn_to_ask'
      db.session.commit()
      response = self.client.get(url_for('games.game',game_id=g2.id))
      data = response.get_data(as_text=True)      
      self.assertTrue("Waiting For Opponent to Ask A Question!" in data)

      g2.status = 'waiting_guest_answer'
      db.session.commit()
      response = self.client.get(url_for('games.game',game_id=g2.id))
      data = response.get_data(as_text=True)      
      self.assertTrue("Waiting For Opponent Answer Your Question!" in data)

      # test game information
      self.assertTrue('10 Points' in data)
      self.assertTrue('10 Points' in data)
      self.assertTrue('Question' in data)
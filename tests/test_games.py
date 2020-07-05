from base_cases import FlaskClientTestCase
from flask import url_for
from app.models import Drawing,Game,Question,User
from app import db

class FlaskGamesTestCase(FlaskClientTestCase):
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

      g2.status = 'in_progress'
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

      g2.status = 'author'
      db.session.commit()
      response = self.client.get(url_for('games.game',game_id=g2.id))
      data = response.get_data(as_text=True)      
      self.assertTrue('Congratulations, You Have Won!' in data)
      self.assertTrue('Send Question' in data)

      g2.status = 'guest'
      db.session.commit()
      response = self.client.get(url_for('games.game',game_id=g2.id))
      data = response.get_data(as_text=True)      
      self.assertTrue('You Have Lost.' in data)

      g2.status = 'in_progress'
      g2.turn = 'waiting_author_answer'
      db.session.commit()
      response = self.client.get(url_for('games.game',game_id=g2.id))
      data = response.get_data(as_text=True)      
      self.assertTrue("Answer Your Opponent's Question!" in data)

      g2.turn = 'guest'
      db.session.commit()
      response = self.client.get(url_for('games.game',game_id=g2.id))
      data = response.get_data(as_text=True)      
      self.assertTrue("Waiting For Opponent to Ask A Question!" in data)

      g2.turn = 'waiting_guest_answer'
      db.session.commit()
      response = self.client.get(url_for('games.game',game_id=g2.id))
      data = response.get_data(as_text=True)      
      self.assertTrue("Waiting For Opponent Answer Your Question!" in data)

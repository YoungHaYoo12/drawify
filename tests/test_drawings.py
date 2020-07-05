from base_cases import FlaskClientTestCase
from flask import url_for
from app.models import Drawing,User
from app import db

class FlaskDrawingsTestCase(FlaskClientTestCase):
  def test_remove_from_display(self):
    u1 = User(username='one',email='one@one.com',password='one')
    d1 = Drawing(filename='d1')
    d2 = Drawing(filename='d2')
    d1.user = u1
    db.session.add_all([u1,d1,d2])
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )

      # invalid drawing
      response = self.client.get(url_for('drawings.remove_from_display',drawing_id=100))
      self.assertEqual(response.status_code,404)

      # drawing not belonging to user
      response = self.client.get(url_for('drawings.remove_from_display',drawing_id=2))
      self.assertEqual(response.status_code,403)

      # drawing already not on display 
      self.assertFalse(d1.display)
      response = self.client.get(url_for('drawings.remove_from_display',drawing_id=1),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('Drawing Not Currently On Display' in data)
      self.assertFalse(d1.display)

      # success
      d1.display = True
      db.session.commit()
      self.assertTrue(d1.display)
      response = self.client.get(url_for('drawings.remove_from_display',drawing_id=1),follow_redirects=True)
      self.assertFalse(d1.display)

  def test_add_to_display(self):
    u1 = User(username='one',email='one@one.com',password='one')
    d1 = Drawing(filename='d1')
    d2 = Drawing(filename='d2')
    d1.user = u1
    db.session.add_all([u1,d1,d2])
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )

      # invalid drawing
      response = self.client.get(url_for('drawings.add_to_display',drawing_id=100))
      self.assertEqual(response.status_code,404)

      # drawing not belonging to user
      response = self.client.get(url_for('drawings.add_to_display',drawing_id=2))
      self.assertEqual(response.status_code,403)

      # successful add to display 
      self.assertFalse(d1.display)
      response = self.client.get(url_for('drawings.add_to_display',drawing_id=1),follow_redirects=True)
      self.assertTrue(d1.display)

      # drawing already on display
      self.assertTrue(d1.display)
      response = self.client.get(url_for('drawings.add_to_display',drawing_id=1),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('Drawing Already On Display' in data)
      self.assertTrue(d1.display)

  def test_drawing(self):
    u1 = User(username='one',email='one@one.com',password='one')
    d1 = Drawing(filename='d1')
    d2 = Drawing(filename='d2')
    d1.user=u1
    d2.user=u1
    d2.display = True
    db.session.add_all([u1,d1,d2])
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )
      # Invalid Drawing
      response = self.client.get(url_for('drawings.drawing',drawing_id=100))
      self.assertEqual(response.status_code,404)

      # Drawing not on display
      response = self.client.get(url_for('drawings.drawing',drawing_id=1))
      data = response.get_data(as_text=True)
      self.assertTrue('Drawing' in data)
      self.assertTrue('Add to Display' in data)
      self.assertFalse('Remove from Display' in data)

      # Drawing on display
      response = self.client.get(url_for('drawings.drawing',drawing_id=2))
      data = response.get_data(as_text=True)
      self.assertTrue('Drawing' in data)
      self.assertFalse('Add to Display' in data)
      self.assertTrue('Remove from Display' in data)

  def test_draw(self):
    u1 = User(username='one',email='one@one.com',password='one')
    db.session.add(u1)
    db.session.commit()
    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )

      response = self.client.get(url_for('drawings.draw'))
      self.assertEqual(response.status_code,200)

  def test_list(self):
    u1 = User(username='one',email='one@one.com',password='one')
    d1 = Drawing(filename='d1')
    d2 = Drawing(filename='d2')
    d1.user=u1
    d2.user=u1
    db.session.add_all([u1,d1,d2])
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )

      response = self.client.get(url_for('drawings.list'))
      self.assertEqual(response.status_code,200)
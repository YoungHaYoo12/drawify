from base_cases import FlaskClientTestCase
from flask import url_for
from app.models import Drawing,User
from app import db

class FlaskCoreTestCase(FlaskClientTestCase):
  def test_friends(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    u3 = User(username='three',email='three@three.com',password='three')
    db.session.add_all([u1,u2,u3])
    db.session.commit()
    u2.send_friend_request_to(u1)
    u1.accept_friend_request_from(u2)
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )
      # invalid user 
      response = self.client.get(url_for('core.friends',username='invalid'),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('Invalid user' in data)

      # successful display
      response = self.client.get(url_for('core.friends',username='one'))
      data = response.get_data(as_text=True)
      self.assertTrue('two' in data)
      self.assertFalse('three' in data)


  def test_pending_friend_requests(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    u3 = User(username='three',email='three@three.com',password='three')
    db.session.add_all([u1,u2,u3])
    db.session.commit()
    u2.send_friend_request_to(u1)
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )

      response = self.client.get(url_for('core.pending_friend_requests'))
      data = response.get_data(as_text=True)
      self.assertTrue('two' in data)
      self.assertFalse('three' in data)

  def test_index(self):
    response = self.client.get(url_for('core.index'))
    self.assertEqual(response.status_code,200)
  
  def test_remove_friend(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    u3 = User(username='three',email='three@three.com',password='three')
    db.session.add_all([u1,u2,u3])
    db.session.commit()
    u3.send_friend_request_to(u1)
    u1.accept_friend_request_from(u3)
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )

      # Invalid User
      response = self.client.get(url_for('core.remove_friend',username='invalid'),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('Invalid User' in data)

      # When user is not a friend
      self.assertFalse(u1.is_friends_with(u2))
      response = self.client.get(url_for('core.remove_friend',username='two'),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('You Are Currently Not Friends with this User' in data)
      self.assertFalse(u1.is_friends_with(u2))

      # success
      self.assertTrue(u1.is_friends_with(u3))
      response = self.client.get(url_for('core.remove_friend',username='three'),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertFalse(u1.is_friends_with(u3))

  def test_decline_friend_request(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    u3 = User(username='three',email='three@three.com',password='three')
    db.session.add_all([u1,u2,u3])
    db.session.commit()
    u3.send_friend_request_to(u1)
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )

      # Invalid User
      response = self.client.get(url_for('core.decline_friend_request',username='flask'),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('Invalid User' in data)

      # When there is no friend request
      response = self.client.get(url_for('core.decline_friend_request',username='two'),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('You Currently Do Not Have a Friend Request from This User' in data)

      # successful
      self.assertTrue(u3.sent_friend_request_to(u1))
      response = self.client.get(url_for('core.decline_friend_request',username='three'),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('Declined Friend Request' in data)
      self.assertFalse(u3.sent_friend_request_to(u1))

  def test_accept_friend_request(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    u3 = User(username='three',email='three@three.com',password='three')
    db.session.add_all([u1,u2,u3])
    db.session.commit()
    u3.send_friend_request_to(u1)
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )

      # Invalid User
      response = self.client.get(url_for('core.accept_friend_request',username='flask'),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('Invalid User' in data)

      # When there is no friend request
      response = self.client.get(url_for('core.accept_friend_request',username='two'),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('You Currently Do Not Have a Friend Request from This User' in data)
      self.assertFalse(u1.is_friends_with(u2))

      # successful
      response = self.client.get(url_for('core.accept_friend_request',username='three'),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('Successfully Accepted Friend Request' in data)
      self.assertTrue(u1.is_friends_with(u3))

  def test_user(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    u3 = User(username='three',email='three@three.com',password='three')
    u4 = User(username='four',email='four@four.com',password='four')
    display_drawing = Drawing(filename='display_drawing')
    nondisplay_drawing = Drawing(filename='nondisplay_drawing')
    display_drawing.display=True
    nondisplay_drawing.display=False
    display_drawing.user = u1
    nondisplay_drawing.user = u1
    db.session.add_all([u1,u2,u3,u4,display_drawing,nondisplay_drawing])
    db.session.commit()
    u1.send_friend_request_to(u2)
    u3.send_friend_request_to(u1)
    u2.accept_friend_request_from(u1)
    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )

      # check buttons when on own page
      response = self.client.get(url_for('core.user',username='one'))
      self.assertEqual(response.status_code,200)
      data = response.get_data(as_text=True)
      self.assertTrue("1" in data)
      self.assertFalse("Friends With You" in data)
      self.assertFalse("Respond to Friend Request" in data)
      self.assertFalse("Remove Friend" in data)


      # check buttons on friends page
      response = self.client.get(url_for('core.user',username='two'))
      self.assertEqual(response.status_code,200)
      data = response.get_data(as_text=True)
      self.assertTrue("1" in data)
      self.assertTrue("Friends With You" in data)
      self.assertFalse("Respond to Friend Request" in data)
      self.assertTrue("Remove Friend" in data)

      # check buttons on page of user who has sent you a friend request
      response = self.client.get(url_for('core.user',username='three'))
      self.assertEqual(response.status_code,200)
      data = response.get_data(as_text=True)
      self.assertTrue("0" in data)
      self.assertFalse("Friends With You" in data)
      self.assertTrue("Respond to Friend Request" in data)
      self.assertFalse("Remove Friend" in data)

      # check buttons on non-friend and not friend-requested page
      response = self.client.get(url_for('core.user',username='four'))
      self.assertEqual(response.status_code,200)
      data = response.get_data(as_text=True)
      self.assertTrue("0" in data)
      self.assertFalse("Friends With You" in data)
      self.assertFalse("Respond to Friend Request" in data)
      self.assertFalse("Remove Friend" in data)

  def test_send_friend_request(self):
    u1 = User(username='one',email='one@one.com',password='one')
    u2 = User(username='two',email='two@two.com',password='two')
    u3 = User(username='three',email='three@three.com',password='three')
    u4 = User(username='four',email='four@four.com',password='four')
    u5 = User(username='five',email='five@five.com',password='five')
    db.session.add_all([u1,u2,u3,u4,u5])
    db.session.commit()

    u1.send_friend_request_to(u2)
    u2.accept_friend_request_from(u1)
    u1.send_friend_request_to(u3)
    u4.send_friend_request_to(u1)

    db.session.commit()

    with self.client:
      self.client.post(url_for('auth.login'), data=
      { 
        'email': 'one@one.com', 
        'password': 'one' 
      }
      )

      # invalid user 
      response = self.client.get(url_for('core.send_friend_request',username='flask'),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('Invalid User' in data)

      # friending oneself
      response = self.client.get(url_for('core.send_friend_request',username='one'),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('You cannot friend yourself' in data)
      self.assertFalse(u1.sent_friend_request_to(u1))

      # if already friends
      response = self.client.get(url_for('core.send_friend_request',username='two'),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('You Are Already Friends With This User' in data)
      self.assertFalse(u1.sent_friend_request_to(u2))

      # if friend request already sent to this user
      response = self.client.get(url_for('core.send_friend_request',username='three'),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('You Have Already Sent a Friend Request to This User' in data)
      self.assertTrue(u1.sent_friend_request_to(u3))

      # if friend request already received from user 
      response = self.client.get(url_for('core.send_friend_request',username='four'),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('You Have Already Received A Friend Request From This User' in data)
      self.assertFalse(u1.sent_friend_request_to(u4))

      # successful friend request 
      response = self.client.get(url_for('core.send_friend_request',username='five'),follow_redirects=True)
      data = response.get_data(as_text=True)
      self.assertTrue('Successfully Sent Friend Request to User' in data)
      self.assertTrue(u1.sent_friend_request_to(u5))

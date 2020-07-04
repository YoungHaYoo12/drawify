from base_cases import FlaskClientTestCase
from flask import url_for
from app.models import User
from app import db

class FlaskAuthTestCase(FlaskClientTestCase):
  def test_auth_register(self):
    # register a new valid account
    response1 = self.client.post(url_for('auth.register'), data = {
      'email':'one@one.com',
      'username':'one',
      'password':'one',
      'password2':'one'
    },follow_redirects=True)
    self.assertEqual(response1.status_code, 200)
    self.assertTrue("Successfully Registered" in response1.get_data(as_text=True))

    # register with empty data
    response2 = self.client.post(url_for('auth.register'), data= {
      'email':"",
      'username':"",
      'password':"",
      'password2':""
    })
    self.assertNotEqual(response2.status_code, 302)

    # register with invalid email
    response3 = self.client.post(url_for('auth.register'), data = {
      'email':'twotwo.com',
      'username':'two',
      'password':'two',
      'password2':'two'
    })
    self.assertNotEqual(response3.status_code, 302)

    # register with invalid username
    response4 = self.client.post(url_for('auth.register'), data = {
      'email':'two@two.com',
      'username':'',
      'password':'two',
      'password2':'two'
    })
    self.assertNotEqual(response4.status_code, 302)    

    # register with unmatching passwords
    response5 = self.client.post(url_for('auth.register'), data = {
      'email':'two@two.com',
      'username':'two',
      'password':'two',
      'password2':'nottwo'
    })
    self.assertNotEqual(response5.status_code, 302)   

    # register with already existing email
    response6 = self.client.post(url_for('auth.register'), data = {
      'email':'one@one.com',
      'username':'two',
      'password':'two',
      'password2':'nottwo'
    })    
    self.assertNotEqual(response6.status_code,302)

    # register with already existing username
    response7 = self.client.post(url_for('auth.register'), data = {
      'email':'two@two.com',
      'username':'one',
      'password':'two',
      'password2':'nottwo'
    })    
    self.assertNotEqual(response7.status_code,302)    


  def test_auth_login_logout(self):
    # invalid email
    response1 = self.client.post(url_for('auth.login'), data= {
      'email':'notanemail',
      'password':'password'
    })
    self.assertNotEqual(response1.status_code,302)

    # invalid password
    response2 = self.client.post(url_for('auth.login'), data= {
      'email':'one@one.com',
      'password':''
    })
    self.assertNotEqual(response2.status_code,302)

    # unsuccessful login
    response8 = self.client.post(url_for('auth.login'), data= {
      'email':'usernotregistered@email.com',
      'password':'password'
    })
    self.assertNotEqual(response8.status_code,302)
    self.assertTrue("Invalid Username or Password" in response8.get_data(as_text=True))

    # successful login
    user = User(email='one@one.com',username='one',password='one')
    db.session.add(user)
    db.session.commit()
    response9 = self.client.post(url_for('auth.login'), data= {
      'email':'one@one.com',
      'password':'one'
    }, follow_redirects=True)
    self.assertEqual(response9.status_code,200)
    self.assertTrue('Logged In Successfully' in response9.get_data(as_text=True))

    # logout
    response10 = self.client.get(url_for('auth.logout'),follow_redirects=True)
    self.assertEqual(response10.status_code,200)
    self.assertTrue('You Have Been Logged Out' in response10.get_data(as_text=True))

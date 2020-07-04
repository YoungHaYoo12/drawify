from base_cases import FlaskTestCase
from app.models import Drawing,Hint,Question,User
from app import db
from datetime import datetime

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
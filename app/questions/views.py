from app.questions import questions

@questions.route('/')
def test():
  return "Questions Page"
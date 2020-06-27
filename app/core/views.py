from app.core import core

@core.route('/')
def index():
  return "Core Page"
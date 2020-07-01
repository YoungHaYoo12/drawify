from app.games import games

@games.route('/')
def test():
  return "Games Page"
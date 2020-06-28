from flask_script import Manager, Shell
from flask_migrate import Migrate
from app import create_app, db
from app.models import User, Drawing

app = create_app('default')
manager = Manager(app)
Migrate(app,db)


def make_shell_context():
  return dict(app=app,
              db=db,
              User=User,
              Drawing=Drawing)
manager.add_command("shell", Shell(make_context=make_shell_context))


if __name__ == '__main__':
  manager.run()
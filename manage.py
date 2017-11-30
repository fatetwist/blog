# coding=utf-8
from flask_script import Shell, Manager
from app import db
from app import create_app
from app.models import User, Role, Permission, Post, Follow, Comment
from flask_migrate import MigrateCommand, Migrate


app = create_app('default')
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(User=User, Role=Role, db=db, Post=Post, Follow=Follow, Comment=Comment)


manager.add_command('db', MigrateCommand)
manager.add_command('shell', Shell(make_context=make_shell_context))


if __name__ == '__main__':
    manager.run()

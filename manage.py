# from flask_migrate import MigrateCommand, Manager
# from sifter import create_app
#
# manager = Manager(create_app)
#
# manager.add_command('db', MigrateCommand)
#
# if __name__ == '__main__':
#     manager.run()
import os
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand

from sifter_app import app, db



app.config.from_object(os.environ['APP_SETTINGS'])

migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    manager.run()
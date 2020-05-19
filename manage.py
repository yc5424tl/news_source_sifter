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

from sifter_app import app, db, send_all_sources


app.config.from_object(os.environ["APP_SETTINGS"])

all_sources = send_all_sources()
migrate = Migrate(app, db)
manager = Manager(app)

manager.add_command("db", MigrateCommand)
manager.add_command(all_sources)


if __name__ == "__main__":
    manager.run()

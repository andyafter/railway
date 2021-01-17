# flask migrations
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import create_app, db

app = create_app()
manager = Manager(app)

# migrate app and db
Migrate(app, db)
# add data management commands
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests"""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    from models.models import *

    manager.run()

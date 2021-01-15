# flask_migrate管理数据迁移的
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from app import create_app, db

app = create_app()
manager = Manager(app)

# 将当前app,与db注册到Migrate
Migrate(app, db)
# 添加管理数据的命令
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

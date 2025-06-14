import os
from flask_app.battery_app import create_app, babel, db
import unittest
import tempfile

class HomeTestCase(unittest.TestCase):
    def setUp(self):
       test_config = {}
       self.test_db_file = tempfile.mkstemp()[1]
       test_config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + self.test_db_file
       test_config['TESTING'] = True
       test_config['WTF_CSRF_ENABLED'] = False
       self.app = create_app(test_config)
       db.init_app(self.app)
       babel.init_app(self.app)
       with self.app.app_context():
           db.create_all()
       #self.app.register_blueprint(user)
       self.client = self.app.test_client()

    def tearDown(self):
        os.remove(self.test_db_file)

    def test_homepage(self):
        rv = self.client.get('/home')
        self.assertEqual(rv.status_code, 200)

    def test_registration(self):
        ...

    def test_login(self):
        ...

    def test_logout(self):
        ...

#test coverage
import coverage

cov = coverage.coverage()
cov.start()

if __name__ == '__main__':
   try:
       unittest.main()
   finally:
       cov.stop()
       cov.save()
       cov.report()
       cov.html_report(directory='coverage')
       cov.erase()
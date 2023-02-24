import unittest
from datetime import date, timedelta

from app import create_app, db
from app.models import User, Weekend
from config import Config


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'


class UserModelCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app(TestConfig)
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_hashing(self):
        user = User(username='stas', email='stas@mail.com')
        user.set_password('cat')
        self.assertFalse(user.check_password('dog'))
        self.assertTrue(user.check_password('cat'))

    def test_weekends(self):
        u1 = User(username='stas', email='stas@mail.com')
        tomorrow = date.today() + timedelta(days=1)
        day_after_tomorrow = date.today() + timedelta(days=2)
        db.session.add(u1)
        w1 = Weekend(date=tomorrow, user=u1)
        db.session.add(w1)
        db.session.commit()

        self.assertTrue(len(u1.available_time(tomorrow, timedelta(minutes=1))) == 0)
        self.assertFalse(len(u1.available_time(day_after_tomorrow, timedelta(minutes=1))) == 0)

        if __name__ == '__main__':
            unittest.main(verbosity=2)

import os
from dotenv import load_dotenv

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))


class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'

    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATION = False
    SQLALCHEMY_SILENCE_UBER_WARNING = os.environ.get('SQLALCHEMY_SILENCE_UBER_WARNING')

    # Начало рабочего дня, конец рабочего дня (utc)и количество дней доступных для записи наперед
    START_OF_THE_DAY = 6
    END_OF_THE_DAY = 11
    AMOUNT_OF_DAYS = 7
    # Настройки почты
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 25)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['stasyand330@gmail.com']
from datetime import datetime, timedelta, date
from math import ceil

import jwt
from flask import current_app
from flask_login import UserMixin
from sqlalchemy import and_
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    amount_of_days = db.Column(db.Integer)
    begin_of_the_day = db.Column(db.Time)  # Начало рабочего дня
    end_of_the_day = db.Column(db.Time)  # Конец рабочего дня

    services = db.relationship('Service', backref='user', lazy='dynamic')
    weekends = db.relationship('Weekend', backref='user', lazy='dynamic')

    def __repr__(self):
        return f'{self.__class__.__name__}(id={self.id!r}, username={self.username!r})'

    @property
    def weekends_from_today(self) -> list:
        """Выходные начиная с сегодня"""
        return self.weekends.filter(Weekend.date > date.today()).all()

    @property
    def weekends_dates(self) -> list:
        return [weekend.date.date() for weekend in self.weekends]

    @property
    def records(self):
        """Запрос на все записи пользователя"""
        return Record.query.join(Service, Service.id == Record.service_id).filter(Service.user_id == self.id)

    @property
    def records_from_now(self):
        """Запрос на записи пользователя с текущего момента в хронологическом порядке"""
        return self.records.filter(Record.timestamp >= datetime.utcnow()).order_by(Record.timestamp)

    def getting_start_of_the_interval(self, search_date: date) -> datetime | None:
        """Получение начальной временной отметки с учетом даты полученной из календаря и учетом текущего момента
        времени, если выбранный день - это сегодня"""
        # если выходной
        if search_date in self.weekends_dates:
            return None

        now = datetime.utcnow()
        if search_date == now.date():  # если сегодня
            if now.time() >= self.end_of_the_day:  # если рабочий день закончился
                return None
            if self.begin_of_the_day < now.time() < self.end_of_the_day:
                # если во время рабочего дня, то округляем до ближайшего получаса
                hours, minutes = divmod(ceil(now.minute / 30) * 30, 60)
                return (now + timedelta(hours=hours)).replace(minute=minutes, second=0, microsecond=0)
        # если не сегодня или сегодня, но до начала рабочего дня
        return datetime.combine(search_date, self.begin_of_the_day)

    def _all_timestamps_of_the_date(self, start_of_the_interval: datetime) -> list:
        """Список всех временных отметок выбранной даты в хронологическом порядке, включая начало дня, конец дня, а
        также начало и конец всех записей в этот день начиная с указанного момента времени"""
        if start_of_the_interval is None:
            return []

        end_of_the_interval = datetime.combine(start_of_the_interval.date(), self.end_of_the_day)
        # Делаем выборку записей с текущего момента до конца рабочего времени и создаем список временных отметок
        records = self.records.filter(and_(Record.timestamp >= start_of_the_interval,
                                           Record.timestamp < end_of_the_interval)).all()

        # Формируем временные отметки дня в виде списка из начального момента и конца рабочего дня и начала и конца
        # всех записей
        timestamps = [start_of_the_interval, end_of_the_interval]
        for r in records:
            timestamps.extend([r.timestamp, r.timestamp + r.service.duration])
        return sorted(timestamps)

    def available_time(self, search_date: date, service) -> list:
        """Список отметок времени доступных для записи с учетом длительности услуги"""
        timestamps = self._all_timestamps_of_the_date(self.getting_start_of_the_interval(search_date))
        # Идея в том, чтобы двигаться от момента времени на нечетной позиции к моменту с четной позицией
        res = []
        for i in range(0, len(timestamps), 2):
            t = timestamps[i]
            while (t + service.duration) <= timestamps[i + 1]:
                res.append(t)
                t += service.duration

        return res

    def is_time_available(self, checked_time: datetime, service) -> bool:
        """Проверка свободно ли время для записи непосредственно перед записью в БД"""
        start_of_the_interval = datetime.combine(checked_time.date(), self.begin_of_the_day)
        timestamps = self._all_timestamps_of_the_date(start_of_the_interval)
        # Идея в том, чтобы пройти по отметкам в попытках впихнуть момент времени записи с длительностью услуги
        for i in range(0, len(timestamps), 2):
            begin, end = timestamps[i], timestamps[i + 1]
            if begin <= checked_time < end and checked_time + service.duration <= end:
                return True

        return False

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def get_reset_password_token(self, expires_in=600):
        return jwt.encode(
            {'reset_password': self.id, 'exp': datetime.now().timestamp() + expires_in},
            key=current_app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_reset_password_token(token):
        try:
            id = jwt.decode(token, key=current_app.config['SECRET_KEY'], algorithms=['HS256'])['reset_password']
        except:
            return
        return User.query.get(id)


@login.user_loader
def load_user(id):
    return User.query.get(int(id))


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50))
    description = db.Column(db.String(140))
    price = db.Column(db.Integer)
    duration = db.Column(db.Interval)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    records = db.relationship('Record', backref='service', lazy='dynamic')

    @property
    def str_duration(self) -> str:
        """Перевод секунд в часы и минуты строкой"""
        sec = self.duration.seconds
        hour, minute = sec // 3600, sec % 3600 // 60
        str_hour = f'{hour} ч. ' if hour else ''
        str_minute = f' {minute} мин.' if minute else ''
        return (str_hour + str_minute).strip()

    def __repr__(self):
        return f'<{self.__class__.__name__}(id={self.id}, title={self.title!r})'


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    phone = db.Column(db.String(64), index=True)
    timestamp = db.Column(db.DateTime, index=True)
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'))

    def __repr__(self):
        return f'<{self.__class__.__name__}(id={self.id}, name={self.name!r}, phone={self.phone!r},' \
               f'timestamp={self.timestamp!r}, service_id={self.service_id})>'


class Weekend(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, index=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __repr__(self):
        return f'<{self.__class__.__name__}(id={self.id}, date={self.date!r}, user_id={self.user_id!r})'

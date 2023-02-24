from datetime import datetime, timezone, timedelta, date, time

from flask_mail import Message

from app import create_app, db, mail
from app.models import Service, Record, User, Weekend

app = create_app()


@app.shell_context_processor
def make_shell_context():
    return dict(db=db, mail=mail, Message=Message,
                Service=Service, Record=Record, User=User, Weekend=Weekend,
                tz=timezone.utc, datetime=datetime, timedelta=timedelta, date=date, time=time,
                u=User.query.get(1), s=Service.query.get(1),
                today=date.today(), tomorrow=date.today()+timedelta(days=1))

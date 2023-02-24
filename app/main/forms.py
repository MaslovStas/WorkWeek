from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField, SelectField, TimeField
from wtforms.validators import DataRequired, Length, Email, ValidationError

from app.models import User


class ServiceForm(FlaskForm):
    title = StringField('Название', validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[Length(min=0, max=140)])
    price = StringField('Цена, грн.', validators=[DataRequired()])
    duration = StringField('Длительность, мин.', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class RecordForm(FlaskForm):
    service_id = SelectField('Услуга')
    timestamp = StringField('Дата и время', validators=[DataRequired('Укажите дату и время')], id='datepicker')
    name = StringField('Имя', validators=[DataRequired()])
    phone = StringField('Телефон', validators=[DataRequired()])
    submit = SubmitField('Сохранить')


class WeekendForm(FlaskForm):
    weekends = StringField('Выберите дни', id='datepicker')
    submit = SubmitField('Добавить')


class EditingProfile(FlaskForm):
    begin_of_the_day = TimeField('Начало дня', [DataRequired()])
    end_of_the_day = TimeField('Конец дня', [DataRequired()])
    amount_of_days = StringField('Количество дней доступных для резервирования', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Сохранить')

    def __init__(self, original_email, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_email = original_email

    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=self.email.data).first()
            if user is not None:
                raise ValidationError('Введите другой Email')
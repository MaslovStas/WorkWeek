from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, StringField
from wtforms.validators import DataRequired, Length, ValidationError


class ChooseService(FlaskForm):
    radio = RadioField(validators=[DataRequired()])
    submit = SubmitField('Выбрать')


class ConfirmInformation(FlaskForm):
    phone = StringField('0XXXXXXXXX', validators=[DataRequired(), Length(min=10, max=10)])
    name = StringField('Имя', validators=[DataRequired()])
    submit = SubmitField('Оформить запись')

    def validate_phone(self, phone):
        if not phone.data.isdigit() or not phone.data.startswith('0'):
            raise ValidationError(message='Неверный формат номера телефона')

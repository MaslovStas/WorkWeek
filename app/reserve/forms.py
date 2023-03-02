from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, StringField
from wtforms.validators import DataRequired, Length, ValidationError


class ChooseService(FlaskForm):
    radio = RadioField(validators=[DataRequired()])
    submit = SubmitField('Далее')


class ConfirmInformation(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    phone = StringField('Телефон', validators=[DataRequired(), Length(min=10, max=10)])
    submit = SubmitField('Оформить запись')

    def validate_phone(self, phone):
        if not phone.data.isdigit() or not phone.data.startswith('0'):
            raise ValidationError(message='Неверный формат номера телефона')

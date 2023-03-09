from flask_wtf import FlaskForm
from wtforms import RadioField, SubmitField, StringField
from wtforms.validators import DataRequired, Length


class ChooseService(FlaskForm):
    radio = RadioField(validators=[DataRequired()])
    submit = SubmitField('Далее')


class ConfirmInformation(FlaskForm):
    name = StringField('Имя', validators=[DataRequired()])
    phone = StringField('Телефон',
                        validators=[DataRequired(),
                                    Length(min=18, max=18, message="Неккоректно введен номер")])
    submit = SubmitField('Записаться')

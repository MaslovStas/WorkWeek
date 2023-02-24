import json
from datetime import datetime, date

from flask import render_template, redirect, url_for, request, jsonify, session, flash

from app import db
from app.models import Service, Record, User
from app.reserve import bp
from app.reserve.forms import ChooseService, ConfirmInformation


@bp.route('/<int:user_id>', methods=['POST', 'GET'])
def choose_service(user_id):
    user = User.query.get_or_404(user_id)
    form = ChooseService()
    form.radio.choices = [(s.id, {'title': s.title,
                                  'description': s.description,
                                  'duration': s.str_duration,
                                  'price': s.price})
                          for s in user.services.all()]
    if form.validate_on_submit():
        return redirect(url_for('.choose_date', service_id=form.radio.data))

    return render_template('reserve/service.html', title='Выберите услугу', form=form)


@bp.route('/<int:service_id>/date', methods=['POST', 'GET'])
def choose_date(service_id):
    service = Service.query.get_or_404(service_id)
    form = ChooseService()
    if form.is_submitted():
        session['time'] = request.form['radio']  # сохраняем время
        return redirect(url_for('.confirm', service_id=service.id))

    return render_template('reserve/time.html', title='Выберите дату',
                           amount_of_days=service.user.amount_of_days,
                           form=form)


@bp.route('/getting-time', methods=['POST'])
def getting_time():
    # Получаем дату и service_id из post-запроса, декодируем их и возвращаем список доступного времени для записи
    data = json.loads(request.get_data())
    search_date, service_id = data.get('date'), data.get('service_id')
    timestamps = []
    if search_date and service_id:
        service = Service.query.get(service_id)
        timestamps = service.user.available_time(date.fromisoformat(search_date), service)
        print(timestamps)
    return jsonify({'time': timestamps})


@bp.route('/<int:service_id>/date/confirm', methods=['POST', 'GET'])
def confirm(service_id):
    if 'time' not in session:
        flash(message='Пожалуйста, выберите время', category='warning')
        return redirect(url_for('.choose_date', service_id=service_id))

    timestamp = datetime.fromisoformat(session['time']).replace(tzinfo=None)
    service = Service.query.get_or_404(service_id)
    form = ConfirmInformation()
    if form.validate_on_submit():
        session.pop('time')
        # проверка свободного времени непосредственно перед сохранением в БД
        if service.user.is_time_available(timestamp, service):
            record = Record(name=form.name.data,
                            phone=form.phone.data,
                            timestamp=timestamp,
                            service=service)
            db.session.add(record)
            db.session.commit()
            flash(message='Вы успешно записались! Ждем Вас!', category='success')
            return redirect(url_for('.choose_service', user_id=service.user.id))

        flash(message='К сожалению данное время уже занято. Пожалуйста, выберите другое время',
              category='warning')
        return redirect(url_for('.choose_date', service_id=service_id))

    return render_template('reserve/confirm.html', title='Введите данные', form=form, service=service, time=timestamp)

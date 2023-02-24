from datetime import datetime, date, timedelta, timezone

from flask import render_template, redirect, url_for, flash, abort, request
from flask_login import login_required, current_user

from app import db
from app.main import bp
from app.main.forms import ServiceForm, RecordForm, WeekendForm, EditingProfile
from app.models import Service, Record, Weekend, User


@bp.route('/')
def index():
    return render_template('index.html')


@bp.route('/services')
@login_required
def services():
    return render_template('services.html', title='Сервис', services=current_user.services)


@bp.route('/services/create_service', methods=['POST', 'GET'])
@login_required
def create_service():
    form = ServiceForm()
    if form.validate_on_submit():
        service = Service(title=form.title.data,
                          description=form.description.data,
                          price=form.price.data,
                          duration=timedelta(minutes=int(form.duration.data)),
                          user=current_user)
        db.session.add(service)
        db.session.commit()
        flash(message='Услуга успешно создана', category='success')
        return redirect(url_for('.services'))

    return render_template('create_service.html', title='Добавление услуги', form=form)


@bp.route('/services/<int:service_id>/update', methods=['POST', 'GET'])
@login_required
def update_service(service_id):
    service = Service.query.get_or_404(service_id)
    if service not in current_user.services:
        abort(401)

    form = ServiceForm()
    if form.validate_on_submit():
        service.title = form.title.data
        service.duration = timedelta(minutes=int(form.duration.data))
        service.price = form.price.data
        db.session.commit()
        flash(message='Изменения успешно сохранены', category='success')
        return redirect(url_for('.services'))
    elif request.method == 'GET':
        form.title.data = service.title
        form.description.data = service.description
        form.price.data = service.price
        form.duration.data = service.duration // timedelta(minutes=1)

    return render_template('update_service.html', title='Изменения услуги', form=form)


@bp.route('/services/<int:service_id>/delete')
@login_required
def delete_service(service_id):
    service = Service.query.get_or_404(service_id)
    if service not in current_user.services:
        abort(401)

    db.session.delete(service)
    db.session.commit()
    flash(message='Услуга успешно удалена', category='success')
    return redirect(url_for('.services'))


@bp.route('/records')
@login_required
def records():
    return render_template('records.html', title='Мои записи', records=current_user.records_from_now)


@bp.route('/records/create_record', methods=['POST', 'GET'])
@login_required
def create_record():
    form = RecordForm()
    form.service_id.choices = [(service.id, service.title) for service in current_user.services]
    if form.validate_on_submit():
        timestamp = datetime.fromisoformat(form.timestamp.data).astimezone(timezone.utc).replace(tzinfo=None)
        service = Service.query.get(form.service_id.data)
        if current_user.is_time_available(timestamp, service):
            record = Record(name=form.name.data, phone=form.phone.data, timestamp=timestamp, service=service)
            db.session.add(record)
            db.session.commit()
            flash(message='Запись успешно создана', category='success')
            return redirect(url_for('.records'))
        flash(message='Это время уже занято', category='warning')

    return render_template('create_record.html', title='Создание записи', form=form)


@bp.route('/records/<int:record_id>/delete')
@login_required
def delete_record(record_id):
    record = Record.query.get_or_404(record_id)
    if record not in current_user.records_from_now:
        abort(401)

    db.session.delete(record)
    db.session.commit()
    flash(message='Запись успешно отменена', category='success')
    return redirect(url_for('.records'))


@bp.route('/weekends')
@login_required
def weekends():
    return render_template('weekends.html', title='Мои выходные', weekends=current_user.weekends_from_today)


@bp.route('/weekends/create_weekends', methods=['POST', 'GET'])
@login_required
def create_weekends():
    form = WeekendForm()
    if form.validate_on_submit():
        if form.weekends.data:  # если были введены выходные в форме
            weekends_dates = current_user.weekends_dates
            for weekend in form.weekends.data.split(', '):
                weekend_date = date.fromisoformat(weekend)
                if weekend_date not in weekends_dates:  # если такого выходного еще нет
                    weekend = Weekend(date=weekend_date, user=current_user)
                    db.session.add(weekend)
            db.session.commit()
            flash(message='Выходные успешно сохранены', category='success')

        return redirect(url_for('.weekends'))

    return render_template('create_weekends.html', title='Добавление выходных', form=form)


@bp.route('/weekends/<int:weekend_id>/delete')
@login_required
def delete_weekend(weekend_id):
    weekend = Weekend.query.get_or_404(weekend_id)
    if weekend not in current_user.weekends:
        abort(401)

    db.session.delete(weekend)
    db.session.commit()
    flash(message='Выходной успешно удален', category='success')
    return redirect(url_for('.weekends'))


@bp.route('/settings')
@login_required
def settings():
    return render_template('settings.html',
                           title='Мои записи',
                           settings={
                               'Начало дня': User.from_utc_to_local(current_user.begin_of_the_day).strftime('%H:%M'),
                               'Конец дня': User.from_utc_to_local(current_user.end_of_the_day).strftime('%H:%M'),
                               'Число дней доступных для резервирования': current_user.amount_of_days,
                               'Email': current_user.email})


@bp.route('/settings/edit_settings', methods=['POST', 'GET'])
@login_required
def edit_settings():
    form = EditingProfile(current_user.email)
    if form.validate_on_submit():
        current_user.begin_of_the_day = User.from_local_to_utc(form.begin_of_the_day.data)
        current_user.end_of_the_day = User.from_local_to_utc(form.end_of_the_day.data)
        current_user.amount_of_days = form.amount_of_days.data
        current_user.email = form.email.data
        db.session.commit()
        flash(message='Настройки успешно сохранены', category='success')
        return redirect(url_for('.settings'))
    elif request.method == 'GET':
        form.begin_of_the_day.data = User.from_utc_to_local(current_user.begin_of_the_day)
        form.end_of_the_day.data = User.from_utc_to_local(current_user.end_of_the_day)
        form.amount_of_days.data = current_user.amount_of_days
        form.email.data = current_user.email
    return render_template('edit_settings.html', title='Изменение настроек', form=form)

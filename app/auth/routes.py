from flask import render_template, flash, redirect, url_for, request
from flask_login import login_user, logout_user, current_user
from werkzeug.urls import url_parse

from app import db
from app.auth import bp
from app.auth.email import send_password_reset_email
from app.auth.forms import LoginForm, RegistrationForm, ResetPasswordRequestForm, ResetPassword
from app.models import User


@bp.route('/login', methods=['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash(message='Некорректный логин либо пароль', category='danger')
            return redirect(url_for('.login'))
        login_user(user=user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)

    return render_template('auth/login.html', title='Войти', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['POST', 'GET'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data,
                    email=form.email.data,
                    begin_of_the_day=form.begin_of_the_day.data,
                    end_of_the_day=form.end_of_the_day.data,
                    amount_of_days=form.amount_of_days.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash(message='Вы успешно зарегистрировались!', category='success')
        return redirect(url_for('.login'))

    return render_template('auth/register.html', title='Зарегистрироваться', form=form)


@bp.route('/reset_password_request', methods=['POST', 'GET'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash(message='Проверьте свой Email для дальнейших инструкция', category='warning')
        return redirect(url_for('.login'))

    return render_template('auth/reset_password_request.html', title='Сбросить пароль', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))

    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))

    form = ResetPassword()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        db.session.commit()
        flash(message='Пароль успешно изменен', category='success')
        return redirect('.login')

    return render_template('auth/reset_password.html', title='Сбросить пароль', form=form)

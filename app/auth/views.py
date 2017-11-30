# coding=utf-8

from flask import render_template, redirect, url_for, flash, request
from . import auth
from flask_login import login_user, login_required, logout_user, current_user
from .forms import LoginForm, RegistrationForm
from ..models import User, Role
from .. import db
from ..email import send_mail
from ..decorators import  admin_required

@auth.route('/login', methods=['POST', 'GET'])
def login():

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()

        if user is not None and user.verify_password(form.password.data):
            login_user(user,form.remember_me.data)
            flash('登录成功！')
            return redirect(request.args.get('next') or url_for('main.index'))
        flash('错误用户名和密码！')
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('您已经退出登录。')
    q = request.args.get('q')
    if q == 'logout':
        return redirect(url_for('main.index'))
    else:
        return redirect(url_for('auth.login'))

@auth.route('/secret')
@admin_required
def secret():
    return 'Only authenticated users are allowed!'


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        token = user.generate_confirmation_token()
        send_mail('[Flasky]用户激活', form.email.data, 'mail/confirm', user=user, token=token)
        flash('激活邮件已经发送到您的邮箱，请注意查收！')
        return redirect(url_for('main.index'))
    return render_template('auth/register.html', form=form)


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    try:
        if current_user.confirmed:
            return render_template('main.index')
        if current_user.confirm(token):
            flash('你已经成功通过电子邮件确认！谢谢！')
        else:
            flash('链接已经过期或者不合法')
        return redirect(url_for('auth.login'))
    except AttributeError:
        flash('请先登录后重新访问邮件链接进行激活！！')
        return redirect(url_for('auth.login'))


@auth.route('/resend_mail')
@login_required
def resend_mail():
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    token = current_user.generate_confirmation_token()
    send_mail('[Flasky]用户激活', current_user.email, 'mail/confirm', user=current_user, token=token)
    flash('激活邮件已经发送到您的邮箱，请注意查收！')
    return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    return render_template('auth/unconfirmed.html')



@auth.before_app_request
def before_app_request():
    print(request.endpoint)
    if current_user.is_authenticated:
        current_user.ping()
        if not current_user.confirmed and request.endpoint[:5] != 'auth.':
            return redirect(url_for('auth.unconfirmed'))
        if request.endpoint == 'auth.login':
            return redirect(url_for('main.index'))

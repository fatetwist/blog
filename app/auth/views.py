
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
        print('查找角色')

        print('开始创建用户')
        user = User(email=form.email.data, username=form.username.data, password=form.password.data)
        print('创建用户')
        db.session.add(user)
        print('添加用户')
        db.session.commit()
        print('提交数据库')
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


@auth.before_app_request
def before_request():
    print(request.endpoint)
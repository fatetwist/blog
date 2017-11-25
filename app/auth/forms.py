from flask_wtf import Form
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import Required, Length, Email, EqualTo, ValidationError
from ..models import User

class LoginForm(Form):
    email = StringField('Email', validators=[Required(),Length(1,64),Email()])
    password = PasswordField('password', validators=[Required()])
    remember_me = BooleanField('Keep me logged in')
    submit = SubmitField('Log in')

class RegistrationForm(Form):
    email = StringField('Email', validators=[Required(),Length(1,64),Email()])
    username = StringField('username', validators=[Required(), Length(1,64)])
    password = PasswordField('password', validators=[Required(), EqualTo('password2', message='两次输入的密码不一致！')])
    password2 = PasswordField('确认密码', validators=[Required()])
    submit = SubmitField('立即注册')


    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经被注册')


    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名被注册')


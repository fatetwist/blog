# coding=utf-8
import os
basedir = os.path.dirname(os.path.abspath(__file__))



class Config:
    SECRET_KEY = os.urandom(16)
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    MAIL_SERVER = 'smtp.qq.com'
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    print(MAIL_PASSWORD, MAIL_USERNAME)
    MAIL_SENDER = '591210216@qq.com'
    FLASKY_ADMIN = '591210216@qq.com'
    FLASKY_PER_PAGE = 10


username = 'root'
password = '123456'
host = 'localhost'
database = 'blog'


class Development(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'mysql://%s:%s@%s/%s' % (username, password, host, database)
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True


config = {
    'Development':Development,
    'default': Development
}

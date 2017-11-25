from flask_mail import Message
from manage import app
from flask import render_template
from . import mail
from threading import Thread



def send_mail(subject, to, template, **kwargs):
    msg = Message(subject, sender=app.config.get('MAIL_SENDER'), recipients=[to])
    msg.body = render_template(template+'.txt', **kwargs)
    msg.html = render_template(template+'.html', **kwargs)
    thr = Thread(target=send_async_mail, args=[msg])
    thr.start()


def send_async_mail(msg):
    with app.app_context():
        mail.send(msg)

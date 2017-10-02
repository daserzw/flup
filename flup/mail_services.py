# -*- coding: utf-8 -*-
from flask_mail import Message
from flup import mail, app

def send_mail(recipients, subject, body, cc=None):
    msg = Message(
        recipients = recipients,
        subject = subject,
        body = body,
        cc = cc
    )
    return mail.send(msg)

import db
from flask.ext.wtf import Form, Required, Email, TextField
from flask.ext.wtf.html5 import EmailField
from registration import send_registration_email


class RecoverForm(Form):
    email = EmailField("Email", validators=[Required(), Email()])


def do_recover(email):
    userdata = db.Register(email).recover()
    if userdata['status'] == 'registered':
        send_registration_email(userdata['email'], userdata['key'])
        return {'response': 'Your registration email was resent.'}
    elif userdata['status'] == 'verified':
        return {'response': userdata}
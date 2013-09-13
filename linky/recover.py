from flask.ext.wtf import Form, Required, Email
from flask.ext.wtf.html5 import EmailField

import db
import mailgun
from registration import send_registration_email
from . import app


EMAIL_SUBJ = "linkyto.me - Recovering Your Account"

EMAIL_BODY = """
Hello,

Somebody, possibly you, requested a recovery of your account
information.  The following link will take you to your account
on linkyto.me so that you may get your bookmarklet once again.

{}

Regards,
The linkyto.me Team
"""


class RecoverForm(Form):
    email = EmailField("Email", validators=[Required(), Email()])


def send_mail(userdata):
    app.logger.debug('Building recovery email for %s', userdata['email'])
    body = EMAIL_BODY.format('%s/user/%s'
                             % (app.config['BASE_URL'], userdata['key']))
    app.logger.info('Starting send of account recovery email for %s'
                % userdata['email'])
    mailgun.SendEmail(userdata['email'], EMAIL_SUBJ, body).mail_link()


def do_recover(email):
    app.logger.info('Starting account recovery for %s on user request.' % email)
    userdata = db.Register(email).recover()
    if not userdata:
        return False
    elif userdata['status'] == 'registered':
        app.logger.info('Account was previously registered: %s' % email)
        send_registration_email(userdata['email'], userdata['key'])
        return {'response': 'Your registration email was resent.'}
    elif userdata['status'] == 'verified':
        app.logger.info('Account has already been verified: %s' % email)
        send_mail(userdata)
        return {'response': 'Your account information was resent.'}

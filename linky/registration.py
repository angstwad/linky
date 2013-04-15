import threading
import mailgun
from flask.ext.wtf import Form, TextField, Required, Email

REG_EMAIL_SUBJ = "Welcome to linkyto.me"

REG_EMAIL_BODY = """
Hello User!

This email was signed up for an account at linkyto.me.
If you believe you've received this email in error,
or you did not sign up for an account, then you can
safely disregard this email.

If you did sign up for an account, you'll need to click
the following link to have your account validated:
{}

Regards,
The linkyto.me Team
"""

REG_LINK = "http://linkyto.me/verify/{}"


class RegistrationForm(Form):
    email = TextField("Email", validators=[Required(), Email()])


def registration_email_thread(recp, body):
        m = mailgun.SendEmail(recp, REG_EMAIL_SUBJ, body)
        m.mail_link()


def send_registration_email(email, key):
    url = REG_LINK.format(key)
    body = REG_EMAIL_BODY.format(url)
    mail_thread = threading.Thread(target=registration_email_thread,
                                   args=[email, body])
    mail_thread.start()
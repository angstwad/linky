from flask.ext.wtf import Form, TextField, Required, Email
import threading
import mail

REG_EMAIL_SUBJ = "Welcome to linkyto.me"

REG_EMAIL_BODY = """
Hello User!

This email was signed up for an account at linkyto.me.  If you believe you've received this email in error,
or you did not sign up for an account, then you can safely disregard this email.

If you did sign up for an account, you'll need to click the following link to have your account validated:
{}

Regards,
The linkyto.me Team
"""

REG_LINK = "http://linkyto.me/verify/{}"


class registration_form(Form):
    email = TextField("Email", validators=[Required(), Email()])


def registration_email_thread(recp, body):
        m = mail.send_email(recp, REG_EMAIL_SUBJ, body)
        m.mail_link()


def send_registration_email(ver_email, ver_hash):
    url = REG_LINK.format(ver_hash)
    body = REG_EMAIL_BODY.format(url)
    mail_thread = threading.Thread(target=registration_email_thread, args=[ver_email, body])
    mail_thread.start()
import threading

import db
import exc
import config
import mailgun
from . import app


def check_form(form):
    app.logger.debug("Title: %s " % form.get('title'))
    app.logger.debug("Url: %s" % form.get('url'))
    if form.get('title') and form.get('url'):
        return True


def mail_thread(email, json):
    mailgun.SendEmail(email, json['title'], json['url']).mail_link()


def do_email(key, form):
    v = db.Verification(key)
    m = db.Mail(key)
    t = threading.Thread(target=mail_thread, args=[m.email_addr, form])

    if v.check_verification():
        if m.can_send():
            app.logger.info('User approved to send link: %s', m.email_addr)
            if check_form(form):
                app.logger.info('Sending URL email to %s' % m.email_addr)
                t.start()
            else:
                raise exc.FormDoesntLookRightException('Malformed Form: %s'
                                                       % repr(form))
        else:
            raise exc.OverEmailSentLimitException('User over limit of %d '
                                                  'emails per day.' %
                                                  config.MAX_EMAILS_PER_DAY)
    else:
        raise exc.UserNotVerifiedException('User key %s cannot be verified.'
                                           % key)

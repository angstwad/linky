import db
import exc
import config
import mail
import threading
from . import logger


def check_json(json):
    if 'title' in json.keys() and 'url' in json.keys():
        return True
    else:
        return False


def mail_thread(email, json):
    mail.send_email(email, json['title'], json['url']).mail_link()


def send_link_email(key, json):
    v = db.verification(key)
    m = db.mail(key)
    t = threading.Thread(target=mail_thread, args=[m.email_addr, json])

    if v.check_verification():
        if m.can_send() is True:
            logger.info('User approved to send link: %s', m.email_addr)
            if check_json(json):
                logger.info('Sending URL email to %s' % m.email_addr)
                t.start()
            else:
                raise exc.JSONDoesntLookRightException('Malformed JSON: %s'
                                                       % repr(json))
        else:
            raise exc.OverEmailSentLimitException('User over limit of %d '
                                                  'emails per day.' %
                                                  config.MAX_EMAILS_PER_DAY)
    else:
        raise exc.UserNotVerifiedException('User send key %s '
                                           'cannot be verified.' % key)

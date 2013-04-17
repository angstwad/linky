import requests
from requests.auth import HTTPBasicAuth
from . import app, logger


class SendEmail(object):
    def __init__(self, email, subject, content):
        self._apikey = app.config['MAILGUN_API_KEY']
        self._mailgunURL = app.config['MAILGUN_API_URL']

        self.email = email
        self._subject = subject
        self._content = content

        self.mailgun_send_dict = {'from': 'LinkyMail <linkymail@linkyto.me>',
                                  'to': self.email,
                                  'subject':  self._subject,
                                  'text': self._content}

    def _send(self):
        r = requests.post(self._mailgunURL,
                          auth=HTTPBasicAuth('api', self._apikey),
                          data=self.mailgun_send_dict)
        self.mail_status_code = r.status_code
        logger.info('Email sent - <%s> - Mailgun Status Code: %s'
                    % (self.email, self.mail_status_code))

    def mail_link(self):
        self._send()

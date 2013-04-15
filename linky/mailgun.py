import requests
from requests.auth import HTTPBasicAuth
from . import app, logger


class SendEmail(object):
    def __init__(self, email, subject, content):
        self.__apikey = app.config['MAILGUN_API_KEY']
        self.__mailgunURL = app.config['MAILGUN_API_URL']

        self.email = email
        self.__subject = subject
        self.__content = content

        self.mailgun_send_dict = {'from': 'LinkyMail <linkymail@linkyto.me>',
                                  'to': self.email,
                                  'subject':  self.__subject,
                                  'text': self.__content}

    def mail_link(self):
        logger.info('Sending email to %s, Subject: %s' % (self.email,
                                                          self.__subject))
        self.__send()

    def __send(self):
        r = requests.post(self.__mailgunURL,
                          auth=HTTPBasicAuth('api', self.__apikey),
                          data=self.mailgun_send_dict)
        self.mail_send_status = r.status_code

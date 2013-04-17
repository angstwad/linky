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

    def __send(self):
        r = requests.post(self.__mailgunURL,
                          auth=HTTPBasicAuth('api', self.__apikey),
                          data=self.mailgun_send_dict)
        self.mail_status_code = r.status_code
        logger.info('Email sent - <%s> - Mailgun Status Code: %s'
                    % (self.email, self.mail_status_code))

    def mail_link(self):
        self.__send()

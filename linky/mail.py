#!/usr/bin/env python
# -*- coding: utf-8 -*-

import flask
import envelopes
from config import config

BASE_URL = config.BASE_URL


def send_signup_email(signup_key, to_addr):
    subject = "linkyto.me Registration -- Welcome!"
    body = """
Hello,

Somebody, probably you, signed up for an account at linkyto.me.  In order to
verify your account, please click or open the following link:
%(base_url)s/user/verify/%(signup_key)s

Thanks,
The linkyto.me Team
""" % dict(signup_key=signup_key, base_url=BASE_URL)

    envelope = envelopes.Envelope(
        to_addr=to_addr,
        from_addr=config.EMAIL_NOREPLY,
        subject=subject,
        text_body=body
    )
    smtp = envelopes.SMTP(config.SMTP_HOST)
    try:
        smtp.send(envelope)
    except Exception as e:
        flask.current_app.logger.exception(e)
        raise


def send_verified_email(acct_key, to_addr):
    subject = "You're verified on linkyto.me"
    body = """
Hello,

Thanks for verifying your account.  Please proceed to your account page where
you manage your settings and retrieve your bookmarklet:

%(base_url)s/user/%(send_key)s

Thanks,
The linkyto.me Team
""" % dict(base_url=BASE_URL, send_key=acct_key)

    envelope = envelopes.Envelope(
        to_addr=to_addr,
        from_addr=config.EMAIL_NOREPLY,
        subject=subject,
        text_body=body
    )

    smtp = envelopes.SMTP(config.SMTP_HOST)
    try:
        smtp.send(envelope)
    except Exception as e:
        flask.current_app.logger.exception(e)
        raise


def send_link(title, url, to_addr):
    subject = title
    body = """%(url)s

Thanks,
The linkyto.me Team
""" % dict(url=url)

    envelope = envelopes.Envelope(
        to_addr=to_addr,
        from_addr=config.EMAIL_NOREPLY,
        subject=subject,
        text_body=body
    )
    smtp = envelopes.SMTP(config.SMTP_HOST)
    try:
        smtp.send(envelope)
    except Exception as e:
        flask.current_app.logger.exception(e)
        raise
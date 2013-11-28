#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright 2013 Paul Durivage <pauldurivage@gmail.com>
#
# This file is part of linky.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import newrelic.agent
#import os.path
newrelic.agent.initialize('linky/config/newrelic.ini')

import envelopes
import pymongo.errors

from flask.ext import cors
from flask.ext.pymongo import PyMongo
from flask import Flask, g, render_template, request, flash, abort

from config import config
from linky import bookmarklet, forms


app = Flask(__name__)
app.config.from_object(config)
mongo = PyMongo(app)

BASE_URL = config.BASE_URL


@app.route('/')
def index():
    return render_template('index.html')


def _gen_uuid():
    import uuid
    return uuid.uuid4().get_hex()


def _send_signup_email(signup_key, to_addr):
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
        app.logger.exception(e)
        raise


def _send_verified_email(acct_key, to_addr):
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
        app.logger.exception(e)
        raise


def _send_link(title, url, to_addr):
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
        app.logger.exception(e)
        raise



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = forms.SignupForm()
    if form.validate_on_submit():
        app.logger.debug('Form validate')
        email = request.form.get('email')
        if email:
            uuid = _gen_uuid()
            try:
                g.db.users.insert({
                    '_id': email,
                    'signup_key': uuid
                })
            except pymongo.errors.DuplicateKeyError:
                flash('<strong>Hey!</strong> This email has already been used.', 'danger')
                return render_template('signup.html', form=form)
            else:
                _send_signup_email(uuid, email)
                return render_template('signup-success.html')

        else:
            pass
    return render_template('signup.html', form=form)


@app.route('/user/verify/<uuid>')
def verify(uuid):
    result = g.db.users.find_one_or_404({'signup_key': uuid})
    acct_key = _gen_uuid()
    doc = {
        '$set': {
            'verified': True,
            'acct_key': acct_key,
            'signup_key': None,
            'send_limit': 10
        }

    }
    try:
        update = g.db.users.update(result, doc)
    except Exception as e:
        app.logger.exception(e)
        raise
    else:
        _send_verified_email(acct_key, result.get('_id'))
        return render_template('signup-verified.html', user=result,
                               update_status=update)


@app.route('/user/<uuid>')
def user(uuid):
    result = g.db.users.find_one_or_404({'acct_key': uuid})
    url = "%s/user/%s/send" % (BASE_URL, uuid)
    bmk = bookmarklet.bookmarklet(url)
    return render_template('user.html', result=result,
                           url=url, bookmarklet=bmk)


@app.route('/user/<uuid>/send', methods=['POST'])
@cors.origin('*', methods=['POST', 'OPTIONS'])
def send_link(uuid):
    result = g.db.users.find_one_or_404({'acct_key': uuid})
    to_addr = result.get('_id')
    req_url = request.form.get('url')
    req_title = request.form.get('title')
    app.logger.debug(request.form)
    if not req_url and req_title:
        return abort(400)

    try:
        _send_link(req_title, req_url, to_addr)
    except Exception as e:
        return e.message, 500, {}
    else:
        return "", 200, {}


@app.before_request
def before_request():
    mongo.db.authenticate(config.MONGO_USERNAME, config.MONGO_PASSWORD)
    g.db = mongo.db

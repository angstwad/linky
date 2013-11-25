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

from wtforms import TextField
from flask.ext.wtf import Form
from wtforms.validators import Required, Email


class SignupForm(Form):
    email = TextField('Email Address', validators=[Required(), Email()])

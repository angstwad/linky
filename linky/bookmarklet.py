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

import urllib


def bookmarklet(url):
    enc_url = urllib.quote("'%s'" % url)
    bkm_str = "javascript:(function()%%7Bfunction%%20callback()%%7B(function(%%24)%%7Bvar%%20jQuery%%3D%%24%%3B%%24.ajax(%%7Burl%%3A%%20%s%%2Ctype%%3A%%20'post'%%2Cdata%%3A%%20%%7Burl%%3A%%20document.URL%%2Ctitle%%3A%%20document.title%%7D%%2Csuccess%%3A%%20function(data%%2C%%20status)%%20%%7Bconsole.log(data)%%7D%%2Cerror%%3A%%20function(data%%2C%%20status)%%20%%7Bconsole.log(data)%%7D%%7D)%%7D)(jQuery.noConflict(true))%%7Dvar%%20s%%3Ddocument.createElement(%%22script%%22)%%3Bs.src%%3D%%22https%%3A%%2F%%2Fajax.googleapis.com%%2Fajax%%2Flibs%%2Fjquery%%2F1.7.1%%2Fjquery.min.js%%22%%3Bif(s.addEventListener)%%7Bs.addEventListener(%%22load%%22%%2Ccallback%%2Cfalse)%%7Delse%%20if(s.readyState)%%7Bs.onreadystatechange%%3Dcallback%%7Ddocument.body.appendChild(s)%%3B%%7D)()" % enc_url
    return bkm_str

#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 16/7/30 16:00
# @Author  : xavier
from werkzeug.exceptions import Aborter, default_exceptions, HTTPException
from werkzeug.http import HTTP_STATUS_CODES


class UnavailableForLegalReasons(HTTPException):
    code = 451
    description = 'BIG BROTHER IS WATCHING YOU'

default_exceptions[451] = UnavailableForLegalReasons
HTTP_STATUS_CODES[451] = 'Unavailable For Legal Reasons'
abort = Aborter()

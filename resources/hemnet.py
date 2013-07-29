#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Hugo Lindström <hugolm84@gmail.com>


# flask includes
#
from flask import Blueprint, make_response, jsonify, request

#
#system
#
import urllib
hemnet = Blueprint('hemnet', __name__)

## Routes and Handlers ##

@hemnet.route('/hemnet/search/<regex(".*"):query>/<type>')
def search(query, type):
    response = make_response( jsonify(
        {
            'request': query,
            'prefix': '/search/query/type'
        }
    ))
    return response

@hemnet.route('/hemnet')
def welcome():
    response = make_response( jsonify(
        {
            'welcome': "request",
            'prefix': '/hemnet/'
        }
    ))
    return response
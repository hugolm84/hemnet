#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
 * Copyright (C) 2013 Hugo Lindström <hugolm84@gmail.com>
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <http://www.gnu.org/licenses/>.
 *
'''

from flask import Blueprint, make_response, jsonify, request
from parser import hemnet as parser
from utils import cache

hemnet = Blueprint('hemnet', __name__)
hemnetParser = parser.Hemnet()

## Routes and Handlers ##
@hemnet.route('/hemnet/search/<area>/<query>/<type>')
def search(area, query, type):

    queryResponse = hemnetParser.findLocations(query, type, area);
    locationCount = len(queryResponse["locations"]);
    resultCount = 0;
    result = {}
    
    if locationCount != 0 :
        result = hemnetParser.performSearch(queryResponse['search'][int(0)]);
        resultCount = len(result);
    
    response = make_response( jsonify(
        {
            'request': query,
            'resultcount' : resultCount,
            'queryResponse' : queryResponse,
            'prefix': '/search/query/type',
            'locationcount': resultCount,
            'result' : result
        }
    ))

    response.headers = cache.setCacheControl(response.headers, 7200);
    return response

@hemnet.route('/hemnet/locationsearch/<query>')
def locationsearch(query) :

    queryResponse = hemnetParser.findLocations(query, "a")
    response = make_response( jsonify(
        {
            'locations' : queryResponse
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

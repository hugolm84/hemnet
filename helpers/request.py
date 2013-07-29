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

import urllib2
import httplib
import urllib, cookielib
from bs4 import UnicodeDammit
from lxml.html import fromstring, tostring


class RequestRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
    def http_error_404(self, req, fp, code, msg, headers):
        print "error";
    http_error_301 = http_error_303 = http_error_307 = http_error_302


class Request():

    __request = None;

    def __init__(self):
        self._cj = cookielib.CookieJar();
        self._opener = urllib2.build_opener(RequestRedirectHandler, urllib2.HTTPCookieProcessor(self._cj));
        urllib2.install_opener(self._opener);

    def postRequest(self, url, postParams) :
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/html"};
        self.__request = urllib2.Request(url, urllib.urlencode(postParams), headers);
        return self.__request;

    def getResponse(self, url, query = None) :
        if(query is None) :
            print "Getting response from %s" % url;
            self.__request = urllib2.Request(url);
        else : 
            self.__request = urllib2.Request(url, urllib.urlencode(query));

            print "Getting response from %s with query %s" % (url, urllib.urlencode(query));

        response = self._opener.open(self.__request).read();
        return response;
    

    def requestUnicodeDoc(self, url):
        self.__request = urllib2.Request(url)
        return self.getUnicodeDoc(self.__request);


    def getUnicodeDoc(self, request):
        response = self._opener.open(request).read();
        return self.unicodeResponse(response);

    @staticmethod
    def s_unicodeResponse(response):
        dammit = UnicodeDammit(response);
        return fromstring(dammit.unicode_markup);

    def unicodeResponse(self, response):
        dammit = UnicodeDammit(response);
        return fromstring(dammit.unicode_markup);

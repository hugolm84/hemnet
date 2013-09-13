#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (C) 2013 Hugo Lindström <hugolm84@gmail.com>
#
#
# local includes
#
from hemnet import hemnet

#
# flask includes
#
from flask import Flask
from werkzeug.routing import BaseConverter

#
# twisted is our new web backend
#
from twisted.internet import reactor
from twisted.web.server import Site
from twisted.web.wsgi import WSGIResource
# Twisted logging
import sys
from twisted.python import log
from twisted.python.logfile import DailyLogFile

DEBUG = True
app = Flask(__name__)
app.config.from_object(__name__)

# custom url converter
class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]

app.url_map.converters['regex'] = RegexConverter

app.register_blueprint(hemnet)

if __name__ == '__main__':
    if DEBUG :
        log.startLogging(sys.stdout)
        #log.startLogging(DailyLogFile.fromFullPath("logs/charts-twisted.log"))
    # Start the service
    resource = WSGIResource(reactor, reactor.getThreadPool(), app)
    reactor.listenTCP(8080, Site(resource), interface="10.0.1.8")
    reactor.run()


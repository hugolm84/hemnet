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

import logging

class Logger():
    def __init__(self, name, level = logging.DEBUG):
        logger = logging.getLogger(name);
        logger.setLevel(level);
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s');
        
        handlers = [logging.FileHandler("%s.log" % name), logging.StreamHandler()];
        
        for handler in handlers :
            handler.setLevel(logging.DEBUG);
            handler.setFormatter(formatter);
            logger.addHandler(handler);
        
        self.logger = logger;

    def __getattr__(self, name, *args) :
        return getattr(self.logger, name);




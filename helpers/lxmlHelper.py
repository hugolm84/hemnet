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
from bs4 import UnicodeDammit
from lxml.html import fromstring
import re

class LxmlHelper():
    
    @staticmethod
    def xpathToFloat(item):
        try:
            return float(re.sub("([^0-9.])", "", item[0].text_content().replace(",", ".")));
        except Exception:
            return 0.0;
    
    @staticmethod
    def xpathToUnicode(item):
        return UnicodeDammit(item[0].text_content().strip()).unicode_markup;
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

import json
import re
import string
import urllib2
from operator import itemgetter
import httplib
import urllib, cookielib
from lxml.html import fromstring, tostring, parse, submit_form
from lxml.html.clean import clean_html
from bs4 import UnicodeDammit
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s'
)

'''
    @HemnetHTTPRedirect
'''
class HemnetHTTPRedirectHandler(urllib2.HTTPRedirectHandler):
    def http_error_302(self, req, fp, code, msg, headers):
        return urllib2.HTTPRedirectHandler.http_error_302(self, req, fp, code, msg, headers)
    def http_error_404(self, req, fp, code, msg, headers):
        print "error";
    http_error_301 = http_error_303 = http_error_307 = http_error_302

'''
    @Hemnet
    Baseclass for hemnet
'''

class Hemnet() :
    def __init__(self):
        #Base objects for searches and results
        self.baseUrl = "http://www.hemnet.se";
        self.baseSearch = self.baseUrl + "/sok/create";
        self.baseLocation = self.baseUrl + "/locations/show?";
        self.baseResult = self.baseUrl + "/resultat";

        #Basetype, english -> Swedish
        self.translatedTypes = {
            "municipality" : "Kommun",
            "district" : u"Område",
            "postal_city" : "Stadsdel",
            "region" : u"Län",
            "street" : "Gata",
            "city" : "Stad"
        }
        #BaseAverageTypes  -> Swedish
        self.translatedAverageTypes = {
            "age" : u"List ålder",
            "price" : "Medelpris",
            "price-m2" : u"Pris per m²",
            "size" : u"Storlek (m²)",
            "rooms" : "Antal rum",
            "fee" : u"Månadsavgift",
            "price-change-up" : u"Prisökning (%)",
            "price-change-down" : u"Prissäkning (%)"
        }
        
        #Items to get average for        
        self.itemAverageTypes = {
            "age" : 0, 
            "price" : 0, 
            "price-m2" : 0, 
            "size" : 0, 
            "rooms" : 0, 
            "fee" : 0,
            "price-change-up" : 0,
            "price-change-down" : 0
        };

        #Base result format
        self.resultFormat = {
            "totalItems" : 0, 
            "results" : {}
        };
        #We need a cookiejar to store searches
        self._cj = cookielib.CookieJar();
        self._opener = urllib2.build_opener(HemnetHTTPRedirectHandler, urllib2.HTTPCookieProcessor(self._cj));
        urllib2.install_opener(self._opener);
    
    '''
        Searchdata is a formpost in a very specific format
    '''
    def createSearchData(self, data) :
        locationData = [{
            "id": (data.get("id")),
            "name": (data.get("name")),
            "parent_id": (data.get("parent_location").get("id")),
            "parent_name": (data.get("parent_location").get("name"))
        }]

        searchData = {
            "search[location_search]" : locationData,
            "search[location_ids][]": data.get("id"),
            "search[region_id]":-1,
            "search[municipality_ids][]":-1,
            "search[country_id]":0,
            "search[item_types][]": 'all',
            "search[price_min]": '',
            "search[price_max]": '',
            "search[fee_max]": '',
            "search[rooms_min]": '',
            "search[living_area_min]": '',
            "search[keywords]":'',
            "commit": ''
        }
        return searchData;

    '''
        Making a searchRequest requires searchData as params and request via POST
    '''
    def searchRequest(self, query) :
        headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/html"};
        request = urllib2.Request(self.baseSearch, urllib.urlencode(query), headers);
        return request;

    def request(self, url):
        return 
    '''
        Get the response from a url request
    '''
    def getResponse(self, url, query = None) :
        request = urllib2.Request(url, urllib.urlencode(query));
        response = self._opener.open(request).read();
        return response;
    
    '''
    '''
    def requestUnicodeDoc(self, url):
        request = urllib2.Request(url)
        return self.getUnicodeDoc(request);

    '''
        Opens a request and returns a fromstring unicode response
    '''
    def getUnicodeDoc(self, request):
        response = self._opener.open(request).read();
        return self.unicodeResponse(response);

    '''
        Returns UnicodeDammit response as lxml doc
    '''
    def unicodeResponse(self, response):
        dammit = UnicodeDammit(response);
        return fromstring(dammit.unicode_markup);

    '''
        Returns floating point from xpath object
    '''
    def xpathToFloat(self, item):
        if(len(item) > 0):
            return float(re.sub("([^0-9.])", "", item[0].text_content().replace(",", ".")));
        return 0.0;
    '''
        Returns unicode from xpath object
    '''
    def xpathToUnicode(self, item):
        return UnicodeDammit(item[0].text_content().strip()).unicode_markup;

    '''
        Pass a list of keys and a dict of data to caluclate average value for each key
    '''
    def avgByKey(self, keys, data):
        final = {}
        for d in data:
            for k in d.keys():
                if k in keys: 
                    final[k] = final.get(k,0) + d[k]
        for k in final.keys():
            final[k] = final[k]/len(data);
        return final;

    '''
        Find location and return json data from Query string
    '''
    def findLocations(self, query) :
        searchData = []
        jdata = json.loads(self.getResponse(self.baseLocation, {'q' : query}));
        for id, item in enumerate(jdata) :
            searchData.append(self.createSearchData(item.get("location")))
        return {'search' : searchData, 'locations' : jdata};

    '''
        Performs a search request based on searchData
    '''
    def makeSearch(self, searchData):
        try :
            searchResponse = self.getUnicodeDoc(self.searchRequest(searchData));
            result = self.parseResult(searchResponse, self.resultFormat);
            return self.createResultItem(result);
        except Exception,e :
            print "Error: Kunde inte genomföra sökningen. Fel: %s" % e;

    '''
        Parse search results, recursive if theres a next page
    '''
    def parseResult(self, doc, brokers = {}) :
        brokers = self.parseItems(doc.xpath("//div[contains(@class, 'item result')]"), brokers); 
        nextpage = doc.xpath('//a[@class="next_page"]');
        
        try:
            url = nextpage[0].attrib["href"];
            if url is not None:
                print "Parsing %s" % url;
                self.parseResult(self.requestUnicodeDoc(self.baseUrl + url), brokers);
        except Exception,e:
            pass;
        
        return brokers;

    '''
        Formats a result list
    '''
    def createResultItem(self, brokers):
        result = []
        searchItems = []
        for broker in brokers["results"].keys():
            brokerItem = {
                'name' : u'%s' % (broker),
                'percentage': (1.0*len(brokers["results"][broker]["items"])/brokers['totalItems'])*100,
                'items' : brokers["results"][broker]["items"],
                'average' : brokers["results"][broker]["average"]
            };
            result.append(brokerItem);
            
            for item in brokers["results"][broker]["items"]:
                searchItems.append(item);

        #Calculate area averages        
        avg = self.avgByKey(self.itemAverageTypes.keys(), searchItems);
        result = sorted(result, key=lambda k: k['percentage'], reverse=True)         
        resultItem = {
            "totalItems" : brokers["totalItems"],
            "area-avg" : avg,
            "results" : result
        }
        return resultItem;

    def parseItems(self, items, brokers):
        for idx, item in enumerate(items) :
            try:
                broker = item.xpath('.//a[@class="broker"]');
                broker = broker[0].attrib['title'];
                hItem =  {
                    "id" : item.attrib['data-item-id'],
                    "age" : self.xpathToFloat(item.xpath('.//li[@class="age"]/a/span')),
                    "price" : self.xpathToFloat(item.xpath('.//li[@class="price"]/a')),
                    "price-m2" : self.xpathToFloat(item.xpath('.//li[@class="price-per-m2"]/a')),
                    "fee" : self.xpathToFloat(item.xpath('.//li[@class="fee"]/a')),
                    "address" : self.xpathToUnicode(item.xpath('.//li[@class="address"]/a')),
                    "rooms" : self.xpathToFloat(item.xpath('.//li[@class="rooms"]/a')),
                    "size" : self.xpathToFloat(item.xpath('.//li[@class="living-area"]/a')),
                    "type" : self.xpathToUnicode(item.xpath('.//li[@class="item-type"]/a')),
                    "broker" : broker,
                    "price-change-up" : self.xpathToFloat(item.xpath(".//div[contains(@class, 'price-change up')]")),
                    "price-change-down" : self.xpathToFloat(item.xpath(".//div[contains(@class, 'price-change down')]"))
                }
                try:
                    brokers["results"][broker]["items"].append(hItem);
                    brokers["results"][broker]["average"] = self.avgByKey(self.itemAverageTypes.keys(), brokers["results"][broker]["items"]);
                except Exception, e:
                    brokers["results"][broker] = {};
                    brokers["results"][broker]["items"] = [];
                    brokers["results"][broker]["items"].append(hItem);
                    brokers["results"][broker]["average"] = self.itemAverageTypes;

                brokers["totalItems"] = brokers["totalItems"]+1;
            except Exception,e:
                print e
                pass;
        return brokers;

    '''
        Prints location result from locationSearch 
    '''
    def printLocations(self, data):
        print "Hittade %s alternativ" % (len(data));
        for id, item in enumerate(data) :
            item = item.get("location");
            parent = item.get("parent_location");
            print "%s %s %s" % (id, parent.get("name"), self.translatedTypes.get(parent.get("location_type")));
            print "\tTyp: %s" % (self.translatedTypes.get(item.get("location_type")));
            print "\tNamn: %s" % (item.get("name"));

    '''
        Prints Broker item
    '''
    def printBroker(self, id, item):
        name = UnicodeDammit(item.get("name"))
        print "%s\n\t%s" % (id, name.unicode_markup);
        print "\tObjekt\t: %s" % len((item.get("items")));
        print "\tAndel\t: %.2f%s" % (item.get("percentage"), "%");
        print "\tMedel\t:"
        if (len(item.get("items"))) > 1 :
            for key in item.get("average").keys():
                print "\t\t%s\t: %.2f" % (self.translatedAverageTypes.get(key), item.get("average").get(key));
        else:
            print "\t\tn/a";

    def printSearchHeader(self, result):
        print "\tHittade %s antal objekt" % result.get("totalItems");
        print "\tFrån %s antal mäklare" % len(result.get("results"));
        print "\tOmrådesdata:"
        for key in result.get("area-avg").keys():
            print "\t\t%s\t: %.2f" % (self.translatedAverageTypes.get(key), result.get("area-avg").get(key));
    '''
        Use for local testing
    '''
    def parseLocal(self):
        doc = self.unicodeResponse(open("response.html").read());
        brokers = {"totalItems" : 0, "results" : {}};
        result = self.parseItems(doc.xpath("//div[contains(@class, 'item result')]"), brokers); 
        result = self.createResultItem(result);
        self.printSearchHeader(result);
        for idx, item in enumerate(result.get("results")[:10]):
            self.printBroker(idx, item);

    '''
        Menu
    '''
    def menu(self) :
        answer = True;
        while(answer):
            query = raw_input("Sökterm: ");
            queryResponse = self.findLocations(query);
            self.printLocations(queryResponse["locations"]);

            index = raw_input("Välj alternativ: ");
            result = self.makeSearch(queryResponse['search'][int(index)]);
            self.printSearchHeader(result);
            for idx, item in enumerate(result.get("results")[:10]):
                self.printBroker(idx, item);

if __name__ == "__main__":
    hemnet = Hemnet();
    #hemnet.menu();
    hemnet.parseLocal();
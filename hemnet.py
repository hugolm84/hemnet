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
from bs4 import UnicodeDammit

from helpers.logger import Logger
from helpers.request import Request
from helpers.lxmlHelper import LxmlHelper


class Hemnet() :
    def __init__(self):
        self.log = Logger("Hemnet");
        self.request = Request();

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
        self.log.info("Initiated Hemnet");
    
    '''
        Searchdata is a formpost in a very specific format
    '''
    def createSearchFormData(self, data) :
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

    def searchRequest(self, query) :
        return self.request.postRequest(self.baseSearch, query);

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


    def findLocations(self, query) :
        locFormData = []
        locResponse = self.request.getResponse(self.baseLocation, {'q' : query})
        jdata = json.loads(locResponse);
        
        for id, item in enumerate(jdata) :
            formData = self.createSearchFormData(item.get("location"))
            locFormData.append(formData);
        
        return {'search' : locFormData, 'locations' : jdata};


    def performSearch(self, searchData):
        try :
            searchRequest = self.searchRequest(searchData);
            searchResponse = self.request.getUnicodeDoc(searchRequest);
            resultData = self.parseResult(searchResponse, self.resultFormat);
            return self.createResultItem(resultData);
        except Exception,e :
            self.log.critical("Error: Kunde inte genomföra sökningen %s" % e);


    def parseResult(self, doc, brokers = {}) :
        brokers = self.parseItems(doc.xpath("//div[contains(@class, 'item result')]"), brokers); 
        nextpage = doc.xpath('//a[@class="next_page"]');
        
        try:
            url = nextpage[0].attrib["href"];
            if url is not None:
                self.log.info("Parsing %s" % url);
                nextDoc = self.request.requestUnicodeDoc(self.baseUrl + url);
                self.parseResult(nextDoc, brokers);
        except Exception,e:
            self.log.debug("ParseResult %s" % e)
            pass;
        
        return brokers;



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
                    "age" : LxmlHelper.xpathToFloat(item.xpath('.//li[@class="age"]/a/span')),
                    "price" : LxmlHelper.xpathToFloat(item.xpath('.//li[@class="price"]/a')),
                    "price-m2" : LxmlHelper.xpathToFloat(item.xpath('.//li[@class="price-per-m2"]/a')),
                    "fee" : LxmlHelper.xpathToFloat(item.xpath('.//li[@class="fee"]/a')),
                    "address" : LxmlHelper.xpathToUnicode(item.xpath('.//li[@class="address"]/a')),
                    "rooms" : LxmlHelper.xpathToFloat(item.xpath('.//li[@class="rooms"]/a')),
                    "size" : LxmlHelper.xpathToFloat(item.xpath('.//li[@class="living-area"]/a')),
                    "type" : LxmlHelper.xpathToUnicode(item.xpath('.//li[@class="item-type"]/a')),
                    "broker" : broker,
                    "price-change-up" : LxmlHelper.xpathToFloat(item.xpath(".//div[contains(@class, 'price-change up')]")),
                    "price-change-down" : LxmlHelper.xpathToFloat(item.xpath(".//div[contains(@class, 'price-change down')]"))
                }

                try:
                    if hItem["price-m2"] < 1:
                        hItem["price-m2"] = float(hItem["price"]/hItem["size"]);
                except Exception, e:
                    self.log.debug("Failed to calculate price-m2 %s", e)
                    
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
                self.log.debug("ParseItem %s" % e)
                pass;
        return brokers;


    def printLocations(self, data):
        for id, item in enumerate(data) :
            print "%s %s" % (id, self.printableLocation(item))


    def printableLocation(self, item):
        item = item.get("location");
        parent = item.get("parent_location");
        locName = item.get("name");
        locType = self.translatedTypes.get(item.get("location_type"));
        parentLocType = self.translatedTypes.get(parent.get("location_type"));
        parentLocName = parent.get("name");
        return "%s %s\n\tTyp: %s\n\tNamn: %s" % (parentLocName, parentLocType,  locType, locName);
    

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

        #for listItem in item.get("items"):
        #   self.printListItem(listItem);


    def printListItem(self, item):
        print json.dumps(item, indent=4);


    def printSearchHeader(self, result, location):
        print "\tHittade %s antal objekt" % result.get("totalItems");
        print "\tFrån %s antal mäklare" % len(result.get("results"));
        print u"\tSökterm: \n\t\t%s" % self.printableLocation(location).replace('\t', '\t\t');
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


    def menu(self) :
        answer = True;
        while(answer):
            query = raw_input("Sökterm: ");
            queryResponse = self.findLocations(query);
            resultCount = len(queryResponse["locations"]);
            if resultCount != 0 :
                print "Hittade %s alternativ" % (len(queryResponse["locations"]));
                self.printLocations(queryResponse["locations"]);

                index = raw_input("Välj alternativ: ");
                result = self.performSearch(queryResponse['search'][int(index)]);
                self.printSearchHeader(result, queryResponse['locations'][int(index)]);
                for idx, item in enumerate(result.get("results")[:10]):
                    self.printBroker(idx, item);
            else:
                self.log.debug("Failed to find results for %s : %s" % (query, json.dumps(queryResponse)))
                print "Inga alternativ hittades baserat på %s" % query;

if __name__ == "__main__":
    hemnet = Hemnet();
    hemnet.menu();
    #hemnet.parseLocal();
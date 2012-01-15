#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:

"""
    Copyright (C) 2011-2012 eve-irc.net
 
    This file is part of EVErsible.
    EVErsible is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License.
    If not, see <http://www.gnu.org/licenses/>.

    AUTHORS:
     mountainpenguin <pinguino.de.montana@googlemail.com>
     Ghent           <ghentgames@gmail.com>
     petllama        <petllama@gmail.com>
"""

from modules import api
from modules import evedb

API = api.API()

def index(connection, event, config):
    DB = evedb.DUMP()
    
    try:
        dataIn = event.arguments()[0].split(' ', 1)[1].split(' - ')
        itemName = dataIn[0]
        orderType = dataIn[1]
        systemName = dataIn[2]

        systemInfo = DB.getSystemInfoByName(systemName)
        regionID = systemInfo["regionID"]
        itemID = DB.getItemIDByName(itemName)
    except (IndexError, ValueError):
        connection.privmsg(event.target(),
            "Syntax is: %spc [itemname] - [order type (buy|sell)] - [system name] (ex. !pc 425mm Autocannon II - sell - Jita)" % config["bot"]["prefix"])
        itemID = ""

    if not itemID:
        connection.privmsg(event.target(), "Item Unknown")
    else:
        if not regionID:
            EC = API.EveCentral("marketstat", str(itemID))
            buyVolume = EC["buyVolume"]
            buyAvg = EC["buyAvg"]
            buyMax = EC["buyMax"]
            buyMin = EC["buyMin"]
            buyMedian = EC["buyMedian"]

            sellVolume = EC["sellVolume"]
            sellAvg = EC["sellAvg"]
            sellMax = EC["sellMax"]
            sellMin = EC["sellMin"]
            sellMedian = EC["sellMedian"]
            regionName = "Empire"

            if orderType == str.lower("sell"):
                connection.privmsg(event.target(), "Item ID: %s Region: %s Sell Volume: %s Sell Avg: %s Sell Max: %s Sell Min: %s Sell Median: %s"
                % (itemID, regionName, sellVolume, sellAvg, sellMax, sellMin, sellMedian))
            elif orderType == str.lower("buy"):
                connection.privmsg(event.target(), "Item ID:%s  Region: %s Buy Volume: %s Buy Avg: %s Buy Max: %s Buy Min: %s Buy Median: %s"
                % (itemID, regionName, buyVolume, buyAvg, buyMax, buyMin, buyMedian))
            else:
                connection.privmsg(event.target(), "Unknown order type")


        else:
            EC = API.EveCentral("marketstat", str(itemID), str(regionID))
            buyVolume = EC["buyVolume"]
            buyAvg = EC["buyAvg"]
            buyMax = EC["buyMax"]
            buyMin = EC["buyMin"]
            buyMedian = EC["buyMedian"]
 
            sellVolume = EC["sellVolume"]
            sellAvg = EC["sellAvg"]
            sellMax = EC["sellMax"]
            sellMin = EC["sellMin"]
            sellMedian = EC["sellMedian"]
            regionName = systemInfo["regionName"]

            if orderType == str.lower("sell"):
                connection.privmsg(event.target(), "Item ID: %s Region: %s Sell Volume: %s Sell Avg: %s Sell Max: %s Sell Min: %s Sell Median: %s"
                % (itemID, regionName, sellVolume, sellAvg, sellMax, sellMin, sellMedian))
            elif orderType == str.lower("buy"):
                connection.privmsg(event.target(), "Item ID:%s  Region: %s Buy Volume: %s Buy Avg: %s Buy Max: %s Buy Min: %s Buy Median: %s"
                % (itemID, regionName, buyVolume, buyAvg, buyMax, buyMin, buyMedian))
            else:
                connection.privmsg(event.target(), "Unknown order type")


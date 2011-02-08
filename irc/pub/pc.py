#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:

import api
import evedb

API = api.API()
DB = evedb.DUMP()

def index(connection, event, config):

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


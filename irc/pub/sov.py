#!/usr/bin/env python

import api
API = api.API()

def index(connection,event):
    systemName = event.arguments()[0].split()[1]
    sovInfo = API.Map("sov",systemName)
    if sovInfo:
        solarSystemName = sovInfo["solarSystemName"]
        allianceName = sovInfo["allianceName"]
        allianceTicker = sovInfo["allianceTicker"]
        factionName = sovInfo["factionName"]
        corporationName = sovInfo["corporationName"]
        if factionName:
            connection.privmsg(event.target(), "System '%s' is owned by '%s'" % (solarSystemName, factionName))
        else:
            connection.privmsg(event.target(), "System '%s' is owned by '%s' of alliance '%s' (%s)" % (solarSystemName, corporationName, allianceName, allianceTicker))
    else:
        connection.privmsg(event.target(), "System '%s' does not exist" % systemName)
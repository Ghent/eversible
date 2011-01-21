#!/usr/bin/env python

import api
API = api.API()

def index(connection,event):
    systemName = event.arguments()[0].split()[1]
    sovInfo = API.Map("sov",systemName)
    if sovInfo:
        #update API to return system security, regionName and constellationName
        solarSystemName = sovInfo["solarSystemName"]
        allianceName = sovInfo["allianceName"]
        allianceTicker = sovInfo["allianceTicker"]
        factionName = sovInfo["factionName"]
        corporationName = sovInfo["corporationName"]
        if factionName:
            outputMessage = """
                \x02System\x02: %s :: \x1fhttp://evemaps.dotlan.net/system/%s\x1f
                \x032Owner\x03:  %s
            """ % (solarSystemName, solarSystemName, factionName)
            for line in outputMessage.split("\n"):
                connection.privmsg(event.target(), line.strip())
        else:
            outputMessage = """
                \x02System\x02:   %s \x02::\x02 \x1fhttp://evemaps.dotlan.net/system/%s\x1f
                \x039Owner\x03:    %s
                \x035Alliance\x03: %s \x02::\x02 %s
            """ % (solarSystemName, solarSystemName, corporationName, allianceName, allianceTicker)
            for line in outputMessage.split("\n"):
                connection.privmsg(event.target(), line.strip())
    else:
        connection.privmsg(event.target(), "System '\x034%s\x03' does not exist" % systemName)

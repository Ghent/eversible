#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import api
import evedb
from misc import functions


API = api.API()
EVE = evedb.DUMP()

def index(connection,event):
    try:
        systemName = event.arguments()[0].split()[1]
    except IndexError:
        connection.privmsg(event.target(), "Syntax is: sov [system name]")
    else:
        sovInfo = API.Map("sov",systemName)
        if sovInfo:
            #update API to return system security, regionName and constellationName
            solarSystemName = sovInfo["solarSystemName"]
            allianceName = sovInfo["allianceName"]
            allianceTicker = sovInfo["allianceTicker"]
            factionName = sovInfo["factionName"]
            corporationName = sovInfo["corporationName"]

            systemInfo = EVE.getSystemInfoByID(sovInfo["solarSystemID"])
            sec = functions.security(systemInfo=systemInfo)

            securityClass = systemInfo["securityClass"]
            constellationName = systemInfo["constellationName"]
            regionName = systemInfo["regionName"]

            connection.privmsg(event.target(), "\x02System\x02:   \x02%s\x02/\x0310%s\x03/\x032%s\x03 \x02::\x02 \x1fhttp://evemaps.dotlan.net/system/%s\x1f" %
                               (solarSystemName, constellationName, regionName, solarSystemName)
                               )
            if factionName:
                outputMessage = """
                    \x02Owner\x02:    %s
                    \x02Security\x02: %s \x0314(%s)\x03
                """ % (factionName, sec, securityClass)
                for line in outputMessage.split("\n"):
                    connection.privmsg(event.target(), line.strip())
            else:
                outputMessage = """
                    \x02Owner\x02:    %s
                    \x02Alliance\x02: %s \x02[%s]\x02
                    \x02Security\x02: %s \x0314(%s)\x03
                """ % (corporationName, allianceName, allianceTicker, sec, securityClass)
                for line in outputMessage.split("\n"):
                    connection.privmsg(event.target(), line.strip())
        else:
            connection.privmsg(event.target(), "System '\x034%s\x03' does not exist" % systemName)

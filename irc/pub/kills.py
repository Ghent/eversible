#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import locale

import api
import evedb
from misc import functions


API = api.API()
EVE = evedb.DUMP()

def index(connection, event, config):
    locale.setlocale(locale.LC_ALL, config["core"]["locale"])
    try:
        systemName = event.arguments()[0].split()[1]
    except IndexError:
        connection.privmsg(event.target(), "Syntax is: %skills [system name]" % config["bot"]["prefix"])
    else:
        response = API.Map("kills", systemName)
        if not response:
            connection.privmsg(event.target(), "System '%s' is unknown to me" % systemName)
        else:
            shipKills = response["shipKills"]
            podKills = response["podKills"]
            npcKills = response["npcKills"]
            solarSystemName = response["solarSystemName"]

            systemInfo = EVE.getSystemInfoByID(response["solarSystemID"])
            sec = functions.security(systemInfo=systemInfo)

            regionName = systemInfo["regionName"]
            constellationName = systemInfo["constellationName"]

            connection.privmsg(event.target(), "\x02System\x02:  \x02%s\x02/\x0310%s\x03/\x032%s\x03 (%s)" % (solarSystemName, constellationName, regionName, sec))
            connection.privmsg(event.target(), "\x02Ships\x02:   %i" % locale.format("%d", shipKills, True))
            connection.privmsg(event.target(), "\x02Pods\x02:    %i" % locale.format("%d", podKills, True))
            connection.privmsg(event.target(), "\x02NPCs\x02:    %i" % locale.format("%d", npcKills, True))
            #connection.privmsg(event.target(), "In the last hour, there were %i ship kills, %i pod kills and %i NPC kills in system %s" % (shipKills, podKills, npcKills, solarSystemName))

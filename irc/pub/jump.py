#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import api
import evedb
from misc import functions

API = api.API()
DB = evedb.DUMP()
jumpCapableID = [22440, 22428, 22430, 22436, 28352, 23757, 23915, 24483, 23911, 19724, 19722, 19726, 19720, 28848, 28850, 28846, 28844, 23919, 22852, 23913, 23917, 11567, 671, 3764, 23773]

def index(connection, event, config):
    try:
        shipName = event.arguments()[0].split()[1]
        lvlJDC = int(event.arguments()[0].split()[2])
        lvlJFC = int(event.arguments()[0].split()[3])
        lvlJF = int(event.arguments()[0].split()[4])
        systemFrom = event.arguments()[0].split()[5]
        systemTo = event.arguments()[0].split()[6]
    except (IndexError, ValueError):
        connection.privmsg(event.target(),
            "Syntax is: %sjump [ship name] [JDC lvl] [JFC lvl] [JF lvl] [system name] [system name]" % config["bot"]["prefix"])
    else:
        responseShipID = DB.getItemIDByName(shipName)
        responseSystemFromID = DB.getSystemIDByName(systemFrom)
        responseSystemToID = DB.getSystemIDByName(systemTo)
        if not responseSystemFromID:
            connection.privmsg(event.target(), "System '%s' is unknown to me"
                % systemFrom)
        elif not responseSystemToID:
            connection.privmsg(event.target(), "System '%s' is unknown to me"
                % systemTo)
        elif not responseShipID:
            connection.privmsg(event.target(), "Ship '%s' is unknown to me"
                % shipName)
        elif not responseShipID in jumpCapableID:
            connection.privmsg(event.target(), "Ship '%s' not jump capable"
                % shipName)
        elif lvlJDC > 5 or lvlJDC < 0:
            connection.privmsg(event.target(), "JDC level not within acceptable ranges"
                )
        elif lvlJFC > 5 or lvlJFC < 0:
            connection.privmsg(event.target(), "JFC level not within acceptable ranges"
                )
        elif lvlJF > 5 or lvlJF < 0:
            connection.privmsg(event.target(), "JF level not within acceptable ranges"
                )
        elif DB.getSystemInfoByID(responseSystemFromID)["security"] >= 0.5:
            connection.privmsg(event.target(), "System of Origin must be > 0.0"
                )
        elif DB.getSystemInfoByID(responseSystemToID)["security"] >= 0.5:
            connection.privmsg(event.target(), "Destination sytem must be > 0.0"
                )

        else:
            systemNameFrom = DB.getSystemNameByID(responseSystemFromID)
            systemSecFrom = functions.security(responseSystemFromID)
            systemNameTo = DB.getSystemNameByID(responseSystemToID)
            systemSecTo = functions.security(responseSystemToID)
            shipName = DB.getItemNameByID(responseShipID)
            sytemSecFromChk = DB.getSystemInfoByID(responseSystemFromID)["security"]
            systemSecToChk =  DB.getSystemInfoByID(responseSystemToID)["security"]

            outputMessage = """
                \x02Origin\x02:     %s (%s)
                \x02Endpoint\x02:   %s (%s)
                \x02Ship\x02:       %s  \x0314[JDC: %s, JFC: %s, JF: %s]\x03
                \x02Jump Route\x02: \x1fhttp://evemaps.dotlan.net/jump/%s,%s%s%s/%s:%s\x1f
            """ % (systemNameFrom, systemSecFrom, systemNameTo, systemSecTo,
                  shipName, lvlJDC, lvlJFC, lvlJF, shipName, lvlJDC, lvlJFC,
                  lvlJF, systemNameFrom, systemNameTo)
            for line in outputMessage.split("\n"):
                connection.privmsg(event.target(), line.strip())

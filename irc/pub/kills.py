#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import api
import db

API = api.API()
DB = db.DUMP()

def index(connection, event):
    try:
        systemName = event.arguments()[0].split()[1]
    except IndexError:
        connection.privmsg(event.target(), "Syntax is: kills [system name]")
    else:
        response = API.Map("kills", systemName)
        if not response:
            connection.privmsg(event.target(), "System '%s' is unknown to me" % systemName)
        else:
            shipKills = response["shipKills"]
            podKills = response["podKills"]
            npcKills = response["npcKills"]
            solarSystemName = response["solarSystemName"]
            
            systemInfo = DB.getSystemInfoByID(response["solarSystemID"])
            security = systemInfo["security"]
            if security >= 0.5:
                sec = "\x033\x02\x02%.01f\x03" % security
            elif security < 0.5 and security > 0.0:
                sec = "\x037\x02\x02%.01f\x03" % security
            else:
                sec = "\x035\x02\x02%.02f\x03" % security
            
            regionName = systemInfo["regionName"]
            constellationName = systemInfo["constellationName"]
            
            connection.privmsg(event.target(), "\x02System\x02:  \x02%s\x02/\x0310%s\x03/\x032%s\x03 (%s)" % (solarSystemName, constellationName, regionName, sec))
            connection.privmsg(event.target(), "\x02Ships\x02:   %i" % shipKills)
            connection.privmsg(event.target(), "\x02Pods\x02:    %i" % podKills)
            connection.privmsg(event.target(), "\x02NPCs\x02:    %i" % npcKills)
            #connection.privmsg(event.target(), "In the last hour, there were %i ship kills, %i pod kills and %i NPC kills in system %s" % (shipKills, podKills, npcKills, solarSystemName))

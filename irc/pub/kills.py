#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import api

API = api.API()

def index(connection, event):
    try:
        systemName = event.arguments()[0].split()[1]
        print systemName
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
            if (shipKills, podKills, npcKills) == (0,0,0):
                connection.privmsg(event.target(), "In the last hour, there were no kills in system %s" % (solarSystemName))
            else:
                connection.privmsg(event.target(), "In the last hour, there were %i ship kills, %i pod kills and %i NPC kills in system %s" % (shipKills, podKills, npcKills, solarSystemName))

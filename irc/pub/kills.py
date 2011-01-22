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
            connection.privmsg(event.target(), "\x02System\x02 : %s" % solarSystemName)
            connection.privmsg(event.target(), "\x038Ships\x03  : %i" % shipKills)
            connection.privmsg(event.target(), "\x037Pods\x03   : %i" % podKills)
            connection.privmsg(event.target(), "\x034NPCs\x03   : %i" % npcKills)
            #connection.privmsg(event.target(), "In the last hour, there were %i ship kills, %i pod kills and %i NPC kills in system %s" % (shipKills, podKills, npcKills, solarSystemName))

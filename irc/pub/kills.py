#!/usr/bin/env python

import EVE
import traceback

API = EVE.API()

def index(connection, event):
    systemName = event.arguments()[0].split()[1]
    response = API.Map("kills", systemName)
    if not response:
        connection.privmsg(event.target(), "System '%s' is unknown to me" % systemName)
    else:
        shipKills = response["shipKills"]
        podKills = response["podKills"]
        npcKills = response["npcKills"]
        connection.privmsg(event.target(), "In the last hour, there were %i ship kills, %i pod kills and %i NPC kills in system %s" % (shipKills, podKills, npcKills, systemName))
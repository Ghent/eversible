#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:

"""
    Copyright (C) 2011-2012 eve-irc.net
 
    This file is part of EVErsible.
    EVErsible is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License.
    If not, see <http://www.gnu.org/licenses/>.

    AUTHORS:
     mountainpenguin <pinguino.de.montana@googlemail.com>
     Ghent           <ghentgames@gmail.com>
     petllama        <petllama@gmail.com>
"""

import locale

from modules import api
from modules import evedb
from modules.misc import functions


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
            connection.privmsg(event.target(), "\x02Ships\x02:   %s" % locale.format("%d", shipKills, True))
            connection.privmsg(event.target(), "\x02Pods\x02:    %s" % locale.format("%d", podKills, True))
            connection.privmsg(event.target(), "\x02NPCs\x02:    %s" % locale.format("%d", npcKills, True))
            #connection.privmsg(event.target(), "In the last hour, there were %i ship kills, %i pod kills and %i NPC kills in system %s" % (shipKills, podKills, npcKills, solarSystemName))

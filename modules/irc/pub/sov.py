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

from modules import api
from modules import evedb
from modules.misc import functions


API = api.API()

def index(connection,event,config):
    try:
        systemName = event.arguments()[0].split()[1]
    except IndexError:
        connection.privmsg(event.target(), "Syntax is: %ssov [system name]" % config["bot"]["prefix"])
    else:
        EVE = evedb.DUMP()
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

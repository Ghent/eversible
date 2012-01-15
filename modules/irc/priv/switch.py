#!/usr/bin/python

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

from modules import users

def index(connection, event, config):
    sourceHostname = event.source()
    sourceNick = event.source().split("!")[0]
    try:
        switchTo = " ".join(event.arguments()[0].split()[1:]).strip()
    except IndexError:
        switchTo = None
    else:
        USERS = users.DB()
        #check if identified
        details = USERS.retrieveUserByHostname(sourceHostname)
        if not details:
            connection.privmsg(sourceNick, "You must be identified to use this command")
        else:
            if switchTo.lower() == details["characterName"].lower():
                connection.privmsg(sourceNick, "You're already identified as %s!" % switchTo)
                return
            if switchTo:
                #check if alt is valid
                response = USERS.lookupAlt(details["vCode"], details["keyID"], details["characterName"], switchTo)
                if not response:
                    connection.privmsg(sourceNick, "The character \x033\x02\x02%s\x03\x02\x02 hasn't been registered under your account" % switchTo)
                else:
                    check = USERS.addHostname(switchTo, sourceHostname)
                    if check:
                        connection.privmsg(sourceNick, "You have successfully switched characters to \x039\x02\x02%s\x03\x02\x02" % switchTo)
            else:
                #list alts
                alts = USERS.lookForAlts(details["vCode"], details["keyID"])
                if not alts:
                    connection.privmsg(sourceNick, "You appear to have no alts, this is almost certainly an error")
                else:
                    connection.privmsg(sourceNick, "\x02Alts for character %s\x02:" % details["characterName"])
                    for alt in alts:
                        altName = alt[0]
                        if altName == details["characterName"]:
                            connection.privmsg(sourceNick, "\x033\x02%s\x02\x03 <-- current" % altName)
                        else:
                            connection.privmsg(sourceNick, "\x032\x02%s\x03\x03" % altName)

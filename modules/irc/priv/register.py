#!/usr/bin/env python

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
    """
        SYNTAX: register [character name] [user ID] [API key] [password]
    """
    sourceHostname = event.source()
    sourceNick = event.source().split("!")[0]
    try:
        characterName = event.arguments()[0].split()[1]
        userID = event.arguments()[0].split()[2]
        apiKey = event.arguments()[0].split()[3]
        password = event.arguments()[0].split()[4]
    except IndexError:
        connection.privmsg(sourceNick, "Syntax is: %sregister [character name] [user ID] [API key] [password]" % config["bot"]["prefix"])
    else:
        USERS = users.DB()
        response = USERS.createUser(apiKey, userID, characterName, password, sourceHostname)
        if not response[0]:
            connection.privmsg(sourceNick, "Your registration failed with error: %s" % response[1])
        else:
            connection.privmsg(sourceNick, "Your registration was successful, please do not forget your password, it cannot be retrieved")

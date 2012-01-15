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

def index(connection,event, config):
    """ SYNTAX identify [character name] [password] """
    sourceHostName = event.source()
    sourceNick = event.source().split("!")[0]
    try:
        characterName = " ".join(event.arguments()[0].split()[1:-1])
        password = event.arguments()[0].split()[-1]
    except IndexError:
        connection.privmsg(sourceNick, "Correct syntax: %sidentify [character name] [password]" % config["bot"]["prefix"])
    else:
        USERS = users.DB()
        if USERS.testIdentity(characterName, password, sourceHostName):
            connection.privmsg(sourceNick, "You have successfully identified")
        else:
            connection.privmsg(sourceNick, "Incorrect character name or password")
        
        
    

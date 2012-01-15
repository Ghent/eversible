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
from modules import api
import traceback
USERS = users.DB()

def index(connection, event, config):
    """
        Changes saved settings for your registered user
        SYNTAX: update [char name] [keyID] [vCode] [old password] (new password)
    """
    #check user
    sourceHostname = event.source()
    sourceNick = event.source().split("!")[0]
    
    response = USERS.retrieveUserByHostname(sourceHostname)
    
    if not response:
        connection.privmsg(sourceNick, "You are not identified")
    
    else:
        #get args
        try:
            charName = " ".join(event.arguments()[0].split()[1:-2])
            keyID = event.arguments()[0].split()[-2]
            vCode = event.arguments()[0].split()[-1]
        except IndexError:
            connection.privmsg(sourceNick, "SYNTAX: %supdate [char name] [keyID] [new vCode]" % config["bot"]["prefix"])
        else:
            #check details are correct
            try:
                API = api.API(keyID=keyID, vCode=vCode, characterName=charName)
                API.Account("characters")
            except api.APIError:
                connection.privmsg(sourceNick, "Update failed with error: %s" % " ".join(traceback.format_exc().splitlines()[-1].split()[1:]))
            else:
                response = USERS.updateUser(charName, keyID, vCode, sourceHostname)
                
                if response[0]:
                    USERS.removeHostname(sourceHostname)
                    USERS.addHostname(charName, sourceHostname)
                    connection.privmsg(sourceNick, "Your information was updated successfully")
                else:
                    connection.privmsg(sourceNick, "Update failed with error: %s" % response[1])
                #characterName, userID, password, new_apiKey, new_password, hostname
            

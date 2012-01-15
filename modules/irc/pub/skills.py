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

from modules import api
import time
import traceback
from modules.misc import functions
from modules import users

def index(connection,event, config):
    USERS = users.DB()
    #requires limited api key
    
    #check identify
    sourceHostName = event.source()
    sourceNick = event.source().split("!")[0]
    
    response = USERS.retrieveUserByHostname(sourceHostName)
    if not response:
        connection.privmsg(event.target(), "This command requires your limited API key")
        connection.privmsg(event.target(), "Please identify or register")
    else:
        characterName = response["characterName"]
        characterID = response["characterID"]
        keyID = response["keyID"]
        apiKey = response["vCode"]
        
        try:
            API = response["apiObject"]
            skillqueue = API.Char("skillqueue")
        except api.APIError:
            connection.privmsg(event.target(), "There was an error with the API: %s" % " ".join(traceback.format_exc().splitlines()[-1].split()[1:]))
        else:
            messages = ["\x02Skills currently in training for \x033\x02\x02%s\x03\x02:" % characterName]
            
            queuekeys = skillqueue.keys()
            queuekeys.sort()
            
            attributes = API.Char("charsheet")["attributes"]
            
            for i in queuekeys:
                if i == 8:
                    messages += ["\x02 + %i more\x02" % (len(queuekeys) - 8)]
                    break
                level = skillqueue[i]["level"]
                if level == 5:
                    level_roman = "V"
                elif level == 4:
                    level_roman = "IV"
                elif level == 3:
                    level_roman = "III"
                elif level == 2:
                    level_roman = "II"
                elif level == 1:
                    level_roman = "I"
                else:
                    level_roman = "?"
                    
                typeName = skillqueue[i]["typeName"]
                
                needed_attributes = API.Eve("skilltree", typeID=skillqueue[i]["typeID"])
                
                startTime = skillqueue[i]["startTime"]
                endTime = skillqueue[i]["endTime"]
                
                startSP = skillqueue[i]["startSP"]
                endSP = skillqueue[i]["endSP"]
                
                SPtogo = endSP - startSP
                
                SPpersec = (float(attributes[needed_attributes["primaryAttribute"]]) + (float(attributes[needed_attributes["secondaryAttribute"]]) / 2)) / 60
                total_sec = SPtogo / SPpersec
                
                if i == 0:
                    secs_done = time.time() - startTime
                else:
                    secs_done = 0
                secs_to_go = total_sec - secs_done
                                
                SPleft = endSP - (secs_done * SPpersec) - startSP
                
                messages += ["\x02%i\x02: \x1f%s %s\x1f \x02::\x02 %i SP to go \x02::\x02 Time to go: \x033\x02%s\x02\x03" %
                                   (i+1, typeName, level_roman, SPleft, functions.convert_to_human(secs_to_go))
                            ]
            for message in messages:
                connection.privmsg(event.target(), message)

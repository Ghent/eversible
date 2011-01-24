#!/usr/bin/env python

import users
import api
import time

def index(connection,event):
    #requires limited api key
    
    #check identify
    USERS = users.DB()
    sourceHostName = event.source()
    sourceNick = event.source().split("!")[0]
    
    response = USERS.retrieveUserByHostname(sourceHostName)
    if not response:
        connection.privmsg(event.source().split("!")[0], "This command requires your limited API key")
        connection.privmsg(event.source().split("!")[0], "Please identify or register in a private message")
    else:
        characterName = response["characterName"]
        characterID = response["characterID"]
        userID = response["userID"]
        apiKey = response["apiKey"]
        
        try:
            API = api.API(userid=userID, apikey=apiKey, charid=characterID)
            skillqueue = API.Char("skillqueue")
        except api.APIError:
            connection.privmsg(event.source().split("!")[0], "There was an error with the API: %s" % "too lazy to get this info right now")
        else:
            connection.privmsg(event.source().split("!")[0], "\x02Skills currently in training\x02:")
            
            queuekeys = skillqueue.keys()
            queuekeys.sort()
            for i in queuekeys:
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
                startTime = skillqueue[i]["startTime"]
                endTime = skillqueue[i]["endTime"]
                
                def convert_to_human(Time):
                    mins, secs = divmod(Time, 60)
                    hours, mins = divmod(mins, 60)
                    days, hours = divmod(hours, 24)
                    weeks, days = divmod(days, 7)
                    
                    time_str = ""
                    if weeks > 0:
                        time_str += "%iw " % weeks
                    if days > 0:
                        time_str += "%id " % days
                    if hours > 0:
                        time_str += "%ih " % hours
                    if mins > 0:
                        time_str += "%im " % mins
                    if secs > 0:
                        time_str += "%is" % secs
                    return time_str
                    
                started = convert_to_human(time.time() - startTime)
                ended = convert_to_human(endTime - time.time())
                
                SPleft = skillqueue[i]["endSP"] - skillqueue[i]["startSP"]
                
                connection.privmsg(event.source().split("!")[0], "\x02%i\x02: \x1f%s %s\x1f \x02::\x02 %i SP to go" % (i+1, typeName, level_roman, SPleft))
                connection.privmsg(event.source().split("!")[0], "   Started:    \x02%s\x02 ago" % started)
                connection.privmsg(event.source().split("!")[0], "   Time to go: \x033\x02%s\x02\x03" % ended)
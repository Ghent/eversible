#!/usr/bin/env python

import users
import api
import time
import traceback

def index(connection,event):
    
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
    
    USERS = users.DB()
    
    sourceHostName = event.source()
    sourceNick = event.source().split("!")[0]
    
    response = USERS.retrieveUserByHostname(sourceHostName)
    if not response:
        connection.privmsg(event.source().split("!")[0], "This command requires your full API key")
        connection.privmsg(event.source().split("!")[0], "Please identify or register")
    else:
        characterName = response["characterName"]
        characterID = response["characterID"]
        userID = response["userID"]
        apiKey = response["apiKey"]
        
        try:
            API = api.API(userid=userID, apikey=apiKey, charid=characterID)
            mailheaders = API.Char("mail")
        except api.APIError:
            connection.privmsg(souceNick, "There was an error with the API: %s" % " ".join(traceback.format_exc().splitlines()[-1].split()[1:]))
        else:
            mailkeys = mailheaders.keys()
            mailkeys.sort()
            mailkeys.reverse()
            first5 = mailkeys[:5]

            connection.privmsg(sourceNick, "\x02Latest 5 mails\x02:")
            
            count = 1
            for header in first5:
                title = mailheaders[header]["title"]
                From = mailheaders[header]["senderName"]
                To = []
                if mailheaders[header]["allianceID"]:
                    To += ["\x033\x02\x02%s (\x02%s\x02)\x03" % (mailheaders[header]["allianceName"], mailheaders[header]["allianceTicker"])]
                if mailheaders[header]["corpID"]:
                    To += ["\x037\x02\x02%s\x03" % mailheaders[header]["corpName"]]
                if mailheaders[header]["toCharacters"]:
                    for charID, value in mailheaders[header]["toCharacters"].iteritems():
                        To += ["\x032\x02%s\x02\x03" % value["characterName"]]
                TO = ",".join(To)
                
                timeSent = time.time() - mailheaders[header]["sentDate"]
                human_time = convert_to_human(timeSent)
                connection.privmsg(sourceNick, "    \x02%i\x02: \x1f%s\x1f from %s to %s (%s ago)" % (count, title, From, TO, human_time))
                count += 1
#!/usr/bin/python

import users
import api

def index(connection, event):
    #no args
    # perhaps system name in the future
    
    sourceHostName = event.source()
    sourceNick = event.source().split("!")[0]
    USERS = users.DB()
    
    #check if identified
    APItest = USERS.retrieveUserByHostname(sourceHostName)
    
    if not APItest:
        connection.notice(sourceNick, "This command requires your full api key")
        connection.notice(sourceNick, "Please identify or register")
        connection.privmsg(event.target(), "User \x034\x02'%s'\x03\x02 not recognised" % sourceNick)
    else:
        API = APItest["apiObject"]
        try:
            walletdict = API.Char("wallet")
        except api.APIError:
            connection.notice(sourceNick, "This command requires your full API key")
            connection.privmsg(event.target(), "Insufficient permissions")
        else:
            refIDs = walletdict.keys()
            refIDs.sort()
            bounties = {}
            total_bounty = 0
            for refID in refIDs:
                refTypeID = walletdict[refID]["refTypeID"]
                if refTypeID == 85:
                    #bounty prize! \o/
                    kills = walletdict[refID]["_kills_"]
                    for kill in kills:
                        if kill["shipName"] not in bounties.keys():
                            bounties[kill["shipName"]] = kill["count"]
                        else:
                            bounties[kill["shipName"]] += kill["count"]
                    total_bounty += walletdict[refID]["amount"]
            
            #put thousand seperator into total_bounty
            bounty_temp = str(total_bounty).split(".")[0][::-1]
            bounty_rev = ""
            count = 0
            for char in bounty_temp:
                if count == 3:
                    count = 0
                    bounty_rev += ","
                bounty_rev += char
                count += 1
            bounty = "%s.%s" % (bounty_rev[::-1], str(total_bounty).split(".")[1])
            bounties_list = sorted(bounties.items(), key=lambda ship: ship[1], reverse=True)
            connection.privmsg(event.target(), "\x02PvE stats for character \x038\x02\x02%s\x03 in the past week\x02" % APItest["characterName"])
            connection.privmsg(event.target(), "\x02Total bounty earned\x02: \x039\x02\x02%s ISK\x03\x02\x02" % bounty)
            connection.privmsg(event.target(), "\x02Top 5 NPC ships killed:\x02")
            for shiptype in bounties_list[:5]:
                connection.privmsg(event.target(), "\x034\x02%-25s\x03\x02:  \x033\x02\x02%1i\x03" % (shiptype[0], shiptype[1]))
                
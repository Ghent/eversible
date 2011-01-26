#!/usr/bin/python

import users

def index(connection, event):
    #no args
    # perhaps system name in the future
    
    sourceHostName = event.source()
    sourceNick = event.source().split("!")[0]
    USERS = users.DB()
    
    #check if identified
    API = USERS.retrieveUserByHostname(sourceHostName)
    
    if not API:
        connection.notice(sourceNick, "This command requires your full api key")
        connection.notice(sourceNick, "Please identify or register")
        connection.privmsg(event.target(), "User \x034\x02'%s'\x03\x02 not recognised" % sourceNick)
    else:
        walletdict = API.Char("wallet")
        refIDs = walletdict.keys()
        refIDs.sort()
        bounties = {}
        total_bounty = 0
        for refID in refIDs:
            refTypeID = walletdict[refID]
            if refTypeID == 85:
                #bounty prize! \o/
                kills = walletdict[refID]["_kills_"]
                for kill in kills:
                    if kill["shipName"] not in bounties.keys():
                        bounties[kill["shipName"]] = kill["count"]
                    else:
                        bounties[kill["shipName"]] += kill["count"]
                total_bounty += walletdict[refID]["amount"]
        print bounties
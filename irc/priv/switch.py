#!/usr/bin/python

import users

def index(connection, event):
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
            if switchTo:
                #check if alt is valid
                response = USERS.lookupAlt(details["apiKey"], details["userID"], details["characterName"], switchTo)
                if not response:
                    connection.privmsg(sourceNick, "The character \x033\x02\x02%s\x03\x02\x02 hasn't been registered under your account" % switchTo)
                else:
                    check = USERS.addHostname(switchTo, sourceHostname)
                    if check:
                        connection.privmsg(sourceNick, "You have successfully switched characters to \x039\x02\x02%s\x03\x02\x02" % switchTo)
            else:
                #list alts
                alts = USERS.lookForAlts(details["apiKey"], details["userID"])
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
#!/usr/bin/env python

import users

def index(connection,event):
    """ SYNTAX identify [character name] [password] """
    sourceHostName = event.source()
    sourceNick = event.source().split("!")[0]
    try:
        characterName = event.arguments()[0].split()[1]
        password = event.arguments()[0].split()[2]
    except IndexError:
        connection.privmsg(sourceNick, "Correct syntax: identify [character name] [password]")
    else:
        USERS = users.DB()
        if USERS.testIdentity(characterName, password, sourceHostname):
            connection.privmsg(sourceNick, "You have successfully identified")
        else:
            connection.privmsg(sourceNick, "Incorrect character name or password")
        
        
    
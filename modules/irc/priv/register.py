#!/usr/bin/env python

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

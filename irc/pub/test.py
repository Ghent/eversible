#!/usr/bin/env python

import users

def index(connection, event):
    USERS = user.DB()
    
    sourceHostname = event.source()
    response = USERS.retrieveUserByHostname(sourceHostname)
    if response:
        connection.privmsg(event.target(), "Yes! You are %s, and you are registered and identified")
    else:
        connection.privmsg(event.target(), "No :( I have no record of you here")
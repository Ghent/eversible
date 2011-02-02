#!/usr/bin/env python

import users
import api
import traceback
USERS = users.DB()

def index(connection, event):
    """
        Changes saved settings for your registered user
        SYNTAX: update [char name] [user ID] [new API key] [old password] (new password)
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
            charName = event.arguments()[0].split()[1]
            userID = event.arguments()[0].split()[2]
            apiKey = event.arguments()[0].split()[3]
            password = event.arguments()[0].split()[4]
        except IndexError:
            connection.privmsg(sourceNick, "SYNTAX: update [char name] [user ID] [new API key] [old password] (new password)")
        else:
            try:
                new_password = event.arguments()[0].split()[5]
            except IndexError:
                new_password = password
            
            #verify password
            if not USERS.verifyPassword(charName, password):
                connection.privmsg(sourceNick, "Incorrect password")
            else:
                #check details are correct
                API = api.API(userid=userID, apikey=apiKey, characterName=charName)
                try:
                    API.Account("characters")
                except api.APIError:
                    connection.privmsg(sourceNick, "Update failed with error: %s" % " ".join(traceback.format_exc().splitlines()[-1].split()[1:]))
                else:
                    response = USERS.updateUser(charName, userID, password, apiKey, new_password, sourceHostname)
                    
                    if response[0]:
                        USERS.removeHostname(sourceHostname)
                        USERS.addHostname(charName, sourceHostname)
                        connection.privmsg(sourceNick, "Your information was updated successfully")
                    else:
                        connection.privmsg(sourceNick, "Update failed with error: %s" % response[1])
                    #characterName, userID, password, new_apiKey, new_password, hostname
            
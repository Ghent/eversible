#!/usr/bin/env python

import api

API = api.API()

def index(connection, event):
    try:
        systemFrom = event.arguments()[0].split()[1]
	systemTo = event.arguments()[0].split()[2]
    except IndexError:
        connection.privmsg(event.target(), "Syntax is: .route [system name] [system name]")
    else:
        response = API.Map("sov", systemFrom)
	response2 = API.Map("sov", systemTo)
        if not response:
            connection.privmsg(event.target(), "System '%s' is unknown to me" % systemFrom)
	if not response2:
	    connection.privmsg(event.target(), "System '%s' is unkonwn to me" % systemTo)
        else:
		systemNameFrom = response["solarSystemName"]
		systemNameTo = response2["solarSystemName"] 
		connection.privmsg(event.target(), "Route from %s To %s :" % (systemNameFrom, systemNameTo))
	    	connection.privmsg(event.target(), "http://evemaps.dotlan.net/route/%s:%s" % (systemNameFrom, systemNameTo))

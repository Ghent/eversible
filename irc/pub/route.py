#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import api
import db


API = api.API()
DB = db.DUMP()

def index(connection, event):
    try:
        systemFrom = event.arguments()[0].split()[1]
        systemTo = event.arguments()[0].split()[2]
    except IndexError:
        connection.privmsg(event.target(),
            "Syntax is: .route [system name] [system name]")
    else:
        #responseSystemFrom = API.Map("sov", systemFrom)
        #responseSystemTo = API.Map("sov", systemTo)
        responseSystemFromID = DB.getSystemIDByName("systemFrom")
        responseSystemToID = DB.getSystemIDByName("systemTo")
        if not responseSystemFromID:
            connection.privmsg(event.target(), "System '%s' is unknown to me"
                % systemFrom)
        elif not responseSystemToID:
            connection.privmsg(event.target(), "System '%s' is unkonwn to me"
                % systemTo)
        else:
            systemNameFrom = DB.getSystemNameByID(responseSystemFromID)
            systemNameTo = DB.getSystemNameByID(responseSystemToID)
            connection.privmsg(event.target(),
                "Route from %s To %s :"
                % (systemNameFrom, systemNameTo))
            connection.privmsg(event.target(),
                "http://evemaps.dotlan.net/route/%s:%s"
                % (systemNameFrom, systemNameTo))

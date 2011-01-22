#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import api


API = api.API()

def index(connection, event):
    try:
        systemFrom = event.arguments()[0].split()[1]
        systemTo = event.arguments()[0].split()[2]
    except IndexError:
        connection.privmsg(event.target(),
            "Syntax is: .route [system name] [system name]")
    else:
        responseSystemFrom = API.Map("sov", systemFrom)
        responseSystemTo = API.Map("sov", systemTo)
        if not responseSystemFrom:
            connection.privmsg(event.target(), "System '%s' is unknown to me"
                % systemFrom)
        elif not responseSystemTo:
            connection.privmsg(event.target(), "System '%s' is unkonwn to me"
                % systemTo)
        else:
            systemNameFrom = responseSystemFrom["solarSystemName"]
            systemNameTo = responseSystemTo["solarSystemName"]
            connection.privmsg(event.target(),
                "Route from %s To %s :"
                % (systemNameFrom, systemNameTo))
            connection.privmsg(event.target(),
                "http://evemaps.dotlan.net/route/%s:%s"
                % (systemNameFrom, systemNameTo))

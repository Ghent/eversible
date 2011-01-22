#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import api
import db


API = api.API()
DB = db.DUMP()

def index(connection, event):
    try:
        systemFrom, systemTo, autopilot = event.arguments()[0].split()[1:4]
    except IndexError:
        connection.privmsg(event.target(),
            "Syntax is: .route [system name] [system name] [safe or fast]")
    else:
        if not str.lower(autopilot) == "fast":
            autopilot = "safe"

        responseSystemFromID = DB.getSystemIDByName(systemFrom)
        responseSystemToID = DB.getSystemIDByName(systemTo)
        if not responseSystemFromID:
            connection.privmsg(event.target(), "System '%s' is unknown to me"
                % systemFrom)
        elif not responseSystemToID:
            connection.privmsg(event.target(), "System '%s' is unknown to me"
                % systemTo)
        else:
            systemNameFrom = DB.getSystemNameByID(responseSystemFromID)
            systemSecFrom = security(responseSystemFromID)
            systemNameTo = DB.getSystemNameByID(responseSystemToID)
            systemSecTo = security(responseSystemToID)
            outputMessage = """
                \x02Origin\x02:   %s (%s)
                \x02Endpoint\x02: %s (%s)
            """ % (systemNameFrom, systemSecFrom, systemNameTo, systemSecTo)
            for line in outputMessage.split("\n"):
                connection.privmsg(event.target(), line.strip())

            if autopilot == "fast":
                connection.privmsg(event.target(),
                    "\x02Fast Map\x02: \x1fhttp://evemaps.dotlan.net/route/2:%s:%s\x1f"
                    % (systemNameFrom, systemNameTo))
            else:
                connection.privmsg(event.target(),
                    "\x02Safe Map\x02: \x1fhttp://evemaps.dotlan.net/route/%s:%s\x1f"
                    % (systemNameFrom, systemNameTo))

def security(systemID):
    systemInfo = DB.getSystemInfoByID(systemID)
    security = systemInfo["security"]
    if security >= 0.5:
        sec = "\x033\x02\x02%.01f\x03" % security
    elif security < 0.5 and security > 0.0:
        sec = "\x037\x02\x02%.01f\x03" % security
    else:
        sec = "\x035\x02\x02%.02f\x03" % security

    return sec


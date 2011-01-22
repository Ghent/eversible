#!/usr/bin/env python
#
# vim: filetype=python tabstop=2 expandtab:


import api
import db
API = api.API()
DB = db.DUMP()

def index(connection,event):
    try:
        systemName = event.arguments()[0].split()[1]
    except IndexError:
        connection.privmsg(event.target(), "Syntax is: sov [system name]")
    else:
        sovInfo = API.Map("sov",systemName)
        if sovInfo:
            #update API to return system security, regionName and constellationName
            solarSystemName = sovInfo["solarSystemName"]
            allianceName = sovInfo["allianceName"]
            allianceTicker = sovInfo["allianceTicker"]
            factionName = sovInfo["factionName"]
            corporationName = sovInfo["corporationName"]
            
            systemInfo = DB.getSystemInfoByID(sovInfo["solarSystemID"])
            security = systemInfo["security"]
            if security >= 0.5:
                sec = "\x033\x02\x02%.4f\x03" % security
            elif security < 0.5 and security > 0.0:
                sec = "\x037\x02\x02%.4f\x03" % security
            else:
                sec = "\x035\x02\x02%.4f\x03" % security
                
            securityClass = systemInfo["securityClass"]
                
            if factionName:
                outputMessage = """
                    \x02System\x02:  \x02%s\x02 :: \x1fhttp://evemaps.dotlan.net/system/%s\x1f
                    \x032Owner\x03:   %s
                    \x02Security\x02: %s (%s)
                """ % (solarSystemName, solarSystemName, factionName, sec, securityClass)
                for line in outputMessage.split("\n"):
                    connection.privmsg(event.target(), line.strip())
            else:
                outputMessage = """
                    \x02System\x02:   \x02%s\x02 \x02::\x02 \x1fhttp://evemaps.dotlan.net/system/%s\x1f
                    \x039Owner\x03:    %s
                    \x035Alliance\x03: %s \x02[%s]\x02
                    \x02Security\x02: %s (%s)
                """ % (solarSystemName, solarSystemName, corporationName, allianceName, allianceTicker, sec, securityClass)
                for line in outputMessage.split("\n"):
                    connection.privmsg(event.target(), line.strip())
        else:
            connection.privmsg(event.target(), "System '\x034%s\x03' does not exist" % systemName)

#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


from modules import api
from modules import evedb
from modules.misc import functions


API = api.API()
EVE = evedb.DUMP()


def index(connection, event, config):
    dotlan = "http://evemaps.dotlan.net/route/"

    try:
        data = event.arguments()[0].split()
        origin = data[1]
        endpoint = data[2]

    except IndexError:
        connection.privmsg(event.target(),
            "Syntax is: %sroute [Origin system] [Endpoint system] (Safe, Fast or Low) (Systems to avoid separated by spaces)" % config["bot"]["prefix"])
        connection.privmsg(event.target(),
            "           [ ] = required items      ( ) = optional items     * case insensitive")
    else:
        originID = EVE.getSystemIDByName(origin)
        endpointID = EVE.getSystemIDByName(endpoint)
        if not originID:
            connection.privmsg(event.target(), "Origin system '%s' is unknown to me"
                % origin)
        elif not endpointID:
            connection.privmsg(event.target(), "Endpoint system '%s' is unknown to me"
                % endpoint)
        else:
            # Autopilot DOTLAN strings
            #  "" = Fast Route
            #  :2 = Safe Route
            #  :3 = Lowsec Route
            # Shift the index down 1 so that we know everything left is
            # part of the avoid list.  If Autopilot wasn't defined,
            # don't shift.
            autopilot = ""
            map = ""
            if len(data) > 3:
                if data[3].lower() == "fast":
                    autopilot = ""
                    map = "\x02Fast Map\x02:"
                    data = data[:3] + data[4:]
                elif data[3].lower() == "safe":
                    autopilot = "2:"
                    map = "\x02Safe Map\x02:"
                    data = data[:3] + data[4:]
                elif data[3].lower() == "low":
                    autopilot = "3:"
                    map = "\x02Low Map\x02: "
                    data = data[:3] + data[4:]
                else:
                    map = "\x02Fast Map\x02:"
            else:
                map = "\x02Fast Map\x02:"

            # Get all the system names and skip the ones we don't know
            unknown = []
            count = 0
            for entry in data:
                if entry == config["bot"]["prefix"] + "route":
                    count = count + 1
                    continue
                if not functions.findName(entry, data, count):
                    unknown = unknown + [entry]
                    data = data[:count] + data[count+1:]
                else:
                    count = count + 1

            originSysName = data[1]
            endpointSysName = data[2]

            # Anything at this point should be all avoids so
            # lets construct the URL
            url = dotlan + autopilot + originSysName + ":" + endpointSysName
            avoid = ""
            if len(data) >= 4:
                avoid = ":-" + ":-".join(data[3:])
                url = url + avoid

            # Print the output to IRC
            connection.privmsg(event.target(),
                "\x02Origin\x02:   %s %s" % (data[1], functions.findSecurity(data[1])))
            connection.privmsg(event.target(),
                "\x02Endpoint\x02: %s %s" % (data[2], functions.findSecurity(data[2])))

            if not unknown == []:
                connection.privmsg(event.target(),
                    "\x02Unknown\x02:  \x035" + ", ".join(unknown) + "\x03")

            if not avoid == "":
                avoidsec = []
                for entry in data[3:]:
                    entrysec = functions.findSecurity(entry)
                    if entrysec != None:
                        avoidsec = avoidsec + [entry + " " + entrysec]
                    else:
                        avoidsec = avoidsec + [entry + " " + "\x02(R)\x02"]
                connection.privmsg(event.target(),
                    "\x02Avoids\x02:   " + ", ".join(avoidsec))

            connection.privmsg(event.target(),
                "%s \x1f%s\x1f"
                    % (map, url))

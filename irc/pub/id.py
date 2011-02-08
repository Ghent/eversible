#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import api
import evedb


API = api.API()
DB = evedb.DUMP()

def index(connection, event, config):
    try:
       idSearch = event.arguments()[0].split(None, 1)[1]
    except (IndexError, ValueError):
        connection.privmsg(event.target(),
            "Syntax is: %sid [itemName]" % config["bot"]["prefix"])
    else:
        responseItemName = DB.getItemIDByName(idSearch)
    if not responseItemName:
            connection.privmsg(event.target(), "Item '%s' is unknown to me"
                % idSearch)
    else:
        connection.privmsg(event.target(),
			   "\x02ID of %s\x02: \x1f%s\x1f"
			   % (idSearch, responseItemName))

#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import api
import evedb


API = api.API()
DB = evedb.DUMP()

def index(connection, event):
    try:
        idSearch = " ".join(event.arguments()[0].split()[1:]).strip()
    except (IndexError, ValueError):
        connection.privmsg(event.target(),
            "Syntax is: id [itemName]")
    else:
        responseItemName = DB.getItemIDByName(idSearch)
    if not responseItemName:
            connection.privmsg(event.target(), "Item '%s' is unknown to me"
                % idSearch)
    else:
        connection.privmsg(event.target(),
			   "\x02ID of %s\x02: \x1f%s\x1f"
			   % (idSearch, responseItemName))

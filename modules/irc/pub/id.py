#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:

"""
    Copyright (C) 2011-2012 eve-irc.net
 
    This file is part of EVErsible.
    EVErsible is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    Foobar is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License.
    If not, see <http://www.gnu.org/licenses/>.

    AUTHORS:
     mountainpenguin <pinguino.de.montana@googlemail.com>
     Ghent           <ghentgames@gmail.com>
     petllama        <petllama@gmail.com>
"""

def index(connection, event, config, DB, userdb):
    try:
       idSearch = event.arguments()[0].split(None, 1)[1]
    except (IndexError, ValueError):
        connection.privmsg(event.target(),
            "Syntax is: %sid [itemName]" % config["bot"]["prefix"])
    else:
        responseItemID = DB.getItemIDByName(idSearch)
    if not responseItemID:
            connection.privmsg(event.target(), "Item '%s' is unknown to me"
                % idSearch)
    else:
        responseItemName = DB.getItemNameByID(responseItemID)
        connection.privmsg(event.target(), "\x02ID of %s\x02: \x1f%s\x1f" % (responseItemName, responseItemID))

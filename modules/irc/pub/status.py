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

import locale

from modules import api

API = api.API()

def index(connection, event, config):
    locale.setlocale(locale.LC_ALL, config["core"]["locale"])
    serverstatus = API.Server("status")
    status = serverstatus["status"]
    online = serverstatus["online"]
    servertime = serverstatus["time"].split()[1]
    if status == "Online":
        if online >= 50000:
            players = "\x035 " + locale.format("%d", online, True) + "\x03"
        elif online >= 30000:
            players = "\x037 " + locale.format("%d", online, True) + "\x03"
        else:
            players = "\x033 " + locale.format("%d", online, True) + "\x03"

        message = "\x02Server\x02: \x0311Tranquility\x03  \x02Status\x02: \x039Online\x03  \x02Players\x02:%s  \x02Server Time (GMT)\x02: %s" % (players, servertime)

    elif status == "Offline":
        message = "\x02Server\x02: \x0310Tranquility\x03  \x02Status\x02: \x034Offline\x03"

    connection.privmsg(event.target(), message)

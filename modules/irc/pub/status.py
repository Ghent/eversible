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
from modules.misc import functions

API = api.API()

def index(connection, event, config, evedb, userdb):
    locale.setlocale(locale.LC_ALL, config["core"]["locale"])
    serverstatus = API.Server("status")
    status = serverstatus["status"]
    online = serverstatus["online"]
    servertime = serverstatus["time"].split()[1]
    if status == "Online":
        if online >= 50000:
            players = "[colour=red]" + locale.format("%d", online, True) + "[/colour]"
        elif online >= 30000:
            players = "[colour=yellow]" + locale.format("%d", online, True) + "[/colour]"
        else:
            players = "[colour=green]" + locale.format("%d", online, True) + "[/colour]"

        message = functions.parseIRCBBCode("[b]Server[/b]: [colour=light_cyan]Tranquility[/colour]  [b]Status[/b]: [colour=light_green]Online[/colour]  [b]Players[/b]: %(players)s  [b]Server Time (GMT)[/b]: %(servertime)s" % {
            "players" : players,
            "servertime" : servertime,
        })

    elif status == "Offline":
        message = functions.parseIRCBBCode("[b]Server[/b]: [colour=light_cyan]Tranquility[/colour]  [b]Status[/b]: [colour=light_red]Offline[/colour]")

    connection.privmsg(event.target(), message)

#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import locale

import api

API = api.API()

def index(connection, event):
    #locale.setlocale(locale.LC_ALL, "en_US")
    serverstatus = API.Server("status")
    status = serverstatus["status"]
    online = serverstatus["online"]
    if status == "Online":
        if online >= 50000:
            players = "\x035 " + locale.format("%d", online, True) + "\x03"
            players = players + " \x0314(Shooting fish in a barrel...)\x03"
        elif online >= 30000:
            players = "\x037 " + locale.format("%d", online, True) + "\x03"
            players = players + " \x0314(It's getting a little crowded...)\x03"
        else:
            players = "\x033 " + locale.format("%d", online, True) + "\x03"
            players = players + " \x0314(Space is empty...)\x03"

        message = "\x02Server\x02: \x0311Tranquility\x03  \x02Status\x02: \x039Online\x03  \x02Players\x02:%s" % players

    elif status == "Offline":
        message = "\x02Server\x02: \x0310Tranquility\x03  \x02Status\x02: \x034Offline\x04"

    connection.privmsg(event.target(), message)

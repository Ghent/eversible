#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import api

API = api.API()

def index(connection, event):
    serverstatus = API.Server("status")
    status = serverstatus["status"]
    online = serverstatus["online"]
    if status == "Online":
        message = """
            \x02Server\x02:  \x02Tranquility\x02
            \x02Status\x02:  \x033Online\x033
            \x02Players\02x: \x032%i\x032
        """ % online
    elif status == "Offline":
        message = """
            \x02Server\x02:  \x02Tranquility\x02
            \x02Status\x02:  \x035Offline\x035
        """
        for line in message.split("\n"):
            connection.privmsg(event.target(), line.strip())
    connection.privmsg(event.target(), message)

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
        message = "Server is currently online with %i users" % online
    elif status == "Offline":
        message = "Server is currently offline"
    connection.privmsg(event.target(), message)

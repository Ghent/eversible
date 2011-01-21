#!/usr/bin/env python

import traceback

def index(connection, event):
    try:
        connection.privmsg(event.target(), "Tested string (VERSION) : %s" % VERSION)
    except:
        tb = traceback.format_exc()
        for line in tb.split("\n"):
            connection.privmsg(event.target(), line)
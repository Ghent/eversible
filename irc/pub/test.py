#!/usr/bin/env python

from misc import functions

def index(connection, event):
    args = event.arguments()[0].split()
    
    connection.privmsg(event.target(), functions.setIRCColour(*args))
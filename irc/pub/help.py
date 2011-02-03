#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:

#simple help placeholder. 
def index(connection, event):
    connection.privmsg(event.target(), "Avail commands: bp (blueprint lookup), jump, kills, pve, route, skills, sov, status"
                )

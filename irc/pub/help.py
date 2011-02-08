#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:

#simple help placeholder. 

def index(connection, event, config):
    try:
        helpID = event.arguments()[0].split()[1]
    except (IndexError, ValueError):
        connection.privmsg(event.target(), "Avail commands: bp (blueprint lookup), jump, kills, pve, route, skills, sov, status"
                )
    else:
        if helpID == "bp":
            connection.privmsg(event.target(), "Blueprint- Checks material costs of an item. Syntax: bp [item name]")
        elif helpID == "jump":
            connection.privmsg(event.target(), "Jump planner - uses dotlan to show a ships jump range.")
            connection.privmsg(event.target(), "Syntax: jump [ship name] [JDC lvl] [JFC lvl] [JF lvl] [system name] [system name]")
        elif helpID == "kills":
            connection.privmsg(event.target(), "Kills- Displays latest kills numbers (pvp and pve) for a system")
            connection.privmsg(event.target(), "Syntax is: kills [system name]")
        elif helpID == "pve":
            connection.privmsg(event.target(), "Must be logged in. Displays PVE earnings")
        elif helpID == "route":
            connection.privmsg(event.target(), "Route Planner: uses dotlan to give detailed route information")
            connection.privmsg(event.target(), "Syntax : !route [Origin system] [Endpoint system] (Safe, Fast or Low) (Systems to avoid separated by spaces)")
            connection.privmsg(event.target(), "         [ ] = required items      ( ) = optional items     * case insensitive")
        elif helpID == "skills":
            connection.privmsg(event.target(), "Displays current skills in players queue")
        elif helpID == "sov":
            connection.privmsg(event.target(), "Sov - returns details sov info on a system.")
            connection.privmsg(event.target(), "Syntax: sov [system name]")
        elif helpID == "status":
            connection.privmsg(event.target(), "Returns Server status and time")
        else:
            connection.privmsg(event.target(), "Avail commands: bp (blueprint lookup), jump, kills, pve, route, skills, sov, status")


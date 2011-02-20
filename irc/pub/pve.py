#!/usr/bin/python
#
# vim: filetype=python tabstop=4 expandtab:


import locale
import time
import re

import users
import api
import evedb
DUMP = evedb.DUMP()

from misc import functions

def index(connection, event, config):
    locale.setlocale(locale.LC_ALL, config["core"]["locale"])
    sourceHostName = event.source()
    sourceNick = event.source().split("!")[0]
    USERS = users.DB()

    #check if identified
    APItest = USERS.retrieveUserByHostname(sourceHostName)

    if not APItest:
        connection.notice(sourceNick, "This command requires your full api key")
        connection.notice(sourceNick, "Please identify or register")
        connection.privmsg(event.target(), "User \x034\x02'%s'\x03\x02 not recognised" % sourceNick)
    else:
        API = APItest["apiObject"]
        
        #syntax: pve daterange [system]
        # e.g. : pve 1w F9O-U9
        
        try:
            daterange = event.arguments()[0].split()[1]
        except IndexError:
            daterange = "7d"
        try:
            system = event.arguments()[0].split()[2]
        except IndexError:
            system = None
            
        results = re.search("((?P<weeksago>\d+)w)?((?P<daysago>\d+)d)?((?P<hoursago>\d+)h)?((?P<minutesago>\d+)m)?((?P<secondsago>\d+)s)?", daterange, re.I).groupdict()
        try:
            weeks = int(results["weeksago"])
        except TypeError:
            weeks = 0
        try:
            days = int(results["daysago"])
        except TypeError:
            days = 0
        try:
            hours = int(results["hoursago"])
        except TypeError:
            hours = 0
        try:
            minutes = int(results["minutesago"])
        except TypeError:
            minutes = 0
        try:
            seconds = int(results["secondsago"])
        except TypeError:
            seconds = 0
        delta = seconds + minutes * 60 + hours * 60 * 60 + days * 24 * 60 * 60 + weeks * 7 * 24 * 60 * 60
        starttime = time.time() - delta
        endtime = time.time()
        
        #now check system
        if system:
            system_ID = DUMP.getSystemIDByName(system)
            if not system_ID:
                system_ID = "None"
        else:
            system_ID = None
        
        try:
            walletdict = API.Char("wallet")
        except api.APIError:
            connection.notice(sourceNick, "This command requires your full API key")
            connection.privmsg(event.target(), "Insufficient permissions")
        else:
            refIDs = walletdict.keys()
            refIDs.sort()
            bounties = {}
            total_bounty = 0
            earliest_date = 2147483646
            latest_date = 0
            for refID in refIDs:
                refTypeID = walletdict[refID]["refTypeID"]
                if refTypeID == 85:
                    #bounty prize! \o/
                    bounty_system_id = walletdict[refID]["argID1"]
                    if not system_ID or system_ID == bounty_system_id:
                        
                        bounty_date = walletdict[refID]["date"]
                        if bounty_date > starttime:
                            if bounty_date > latest_date:
                                latest_date = bounty_date
                            if bounty_date < earliest_date:
                                earliest_date = bounty_date
                            kills = walletdict[refID]["_kills_"]
                            
                            for kill in kills:
                                if kill["shipName"] not in bounties.keys():
                                    bounties[kill["shipName"]] = kill["count"]
                                else:
                                    bounties[kill["shipName"]] += kill["count"]
                            total_bounty += walletdict[refID]["amount"]

            bounties_list = sorted(bounties.items(), key=lambda ship: ship[1], reverse=True)
            if total_bounty > 0:
                datestring = "for the past %s" % daterange
                systemstring = ""
                if system:
                    systemstring = "in system [colour=red]%s[/colour]" % DUMP.getSystemNameByID(system_ID)
                connection.privmsg(event.target(), functions.parseIRCBBCode("[b]PvE stats for character [colour=light_yellow]%s[/colour] %s %s [/b]" % (APItest["characterName"], datestring, systemstring)))
                connection.privmsg(event.target(), functions.parseIRCBBCode("[b]Total bounty earned[/b]: [colour=light_green]%s ISK[/colour]" % locale.format("%.2f", total_bounty, True)))
                connection.privmsg(event.target(), "\x02Top 5 NPC ships killed:\x02")
                for shiptype in bounties_list[:5]:
                    connection.privmsg(event.target(), "\x034\x02%-25s\x03\x02:  \x033\x02\x02%1i\x03" % (shiptype[0], shiptype[1]))
                connection.privmsg(event.target(), functions.parseIRCBBCode("[b]Earliest date in range[/b]: %s" % time.strftime("%Y-%b-%d %H:%M", time.gmtime(earliest_date))))
                connection.privmsg(event.target(), functions.parseIRCBBCode("[b]Latest date in range[/b]: %s" % time.strftime("%Y-%b-%d %H:%M", time.gmtime(latest_date))))
            else:
                connection.privmsg(event.target(), functions.parseIRCBBCode("No PvE kills found"))

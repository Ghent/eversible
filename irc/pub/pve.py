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
        except ValueError:
            weeks = 0
        try:
            days = int(results["daysago"])
        except ValueError:
            days = 0
        try:
            hours = int(results["hoursago"])
        except ValueError:
            hours = 0
        try:
            minutes = int(results["minutesago"])
        except ValueError:
            minutes = 0
        try:
            seconds = int(results["secondsago"])
        except ValueError:
            seconds = 0
        delta = seconds + minutes * 60 + hours * 60 * 60 + days * 24 * 60 * 60 + weeks * 7 * 24 * 60 * 60
        starttime = time.time() - delta
        endtime = time.time()
        
        #now check system
        if system:
            system_ID = DUMP.getSystemIDByName(system)
        
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
            connection.privmsg(event.target(), "\x02PvE stats for character \x038\x02\x02%s\x03 between %s and %s\x02" % (APItest["characterName"], time.asctime(time.gmtime(earliest_date)), time.asctime(time.gmtime(latest_date))))
            connection.privmsg(event.target(), "\x02Total bounty earned\x02: \x039\x02\x02%s ISK\x03\x02\x02" % locale.format("%.2f", total_bounty, True))
            if total_bounty != 0:
                connection.privmsg(event.target(), "\x02Top 5 NPC ships killed:\x02")
                for shiptype in bounties_list[:5]:
                    connection.privmsg(event.target(), "\x034\x02%-25s\x03\x02:  \x033\x02\x02%1i\x03" % (shiptype[0], shiptype[1]))

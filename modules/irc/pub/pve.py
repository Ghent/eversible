#!/usr/bin/python
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
import time
import re

from modules import api

from modules.misc import functions

def index(connection, event, config, DUMP, USERS):
    locale.setlocale(locale.LC_ALL, config["core"]["locale"])
    sourceHostName = event.source()
    sourceNick = event.source().split("!")[0]

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
                system_ID = None
        else:
            system_ID = None
        
        try:
            walletdict = API.Char("wallet")
        except api.APIError:
            connection.notice(sourceNick, "This command requires your full API key")
            connection.privmsg(event.target(), "Insufficient permissions")
        else:
            walletSorted = sorted(walletdict.items(), key=lambda x: x[1]["time"], reverse=True)
            kills = {}
            total_bounty = 0
            earliest_date = endtime + 10
            latest_date = starttime - 10
            for transact in walletSorted:
                walletData = transact[1]
                refTypeID = walletData["refTypeID"]
                if refTypeID == 85:
                    #bounty prize! \o/
                    bounty_system_id = walletData["argID1"]
                    if not system_ID or system_ID == bounty_system_id:
                        bounty_date = walletData["time"]
                        if bounty_date > starttime and bounty_date <= endtime:
                            if bounty_date < earliest_date:
                                earliest_date = bounty_date
                            if bounty_date > latest_date:
                                latest_date = bounty_date
                            bountyData = walletData["reason"]
                            for NPC in bountyData.split(",")[:-1]:
                                NPCid = int(NPC.split(":")[0])
                                if NPCid in kills.keys():
                                    prev_count = kills[NPCid]["count"]
                                    kills[NPCid] = {
                                        "shipID" : NPCid,
                                        "shipName" : kills[NPCid]["shipName"],
                                        "count" : prev_count + NPCcount,
                                    }
                                else:
                                    NPCname = DUMP.getItemNameByID(NPCid)
                                    NPCcount = int(NPC.split(":")[1])
                                    kills[NPCid] = {
                                        "shipID" : NPCid,
                                        "shipName" : NPCname,
                                        "count" : NPCcount,
                                    }
                            total_bounty += walletData["amount"]
        
            bounties_list = sorted(kills.items(), key=lambda ship: ship[1]["count"], reverse=True)
            if total_bounty > 0:
                datestring = "for the past %s" % daterange
                systemstring = ""
                if system:
                    systemstring = "in system [colour=red]%s[/colour]" % DUMP.getSystemNameByID(system_ID)
                connection.privmsg(event.target(), functions.parseIRCBBCode("[b]PvE stats for character [colour=light_yellow]%s[/colour] %s %s [/b]" % (APItest["characterName"], datestring, systemstring)))
                connection.privmsg(event.target(), functions.parseIRCBBCode("[b]Total bounty earned[/b]: [colour=light_green]%s ISK[/colour]" % locale.format("%.2f", total_bounty, True)))
                connection.privmsg(event.target(), "\x02Top 5 NPC ships killed:\x02")
                for shiptype in bounties_list[:5]:
                    connection.privmsg(event.target(), "\x034\x02%-25s\x03\x02:  \x033\x02\x02%1i\x03" % (shiptype[1]["shipName"], shiptype[1]["count"]))
                connection.privmsg(event.target(), functions.parseIRCBBCode("[b]Earliest date in range[/b]: %s" % time.strftime("%Y-%b-%d %H:%M", time.gmtime(earliest_date))))
                connection.privmsg(event.target(), functions.parseIRCBBCode("[b]Latest date in range[/b]: %s" % time.strftime("%Y-%b-%d %H:%M", time.gmtime(latest_date))))
            else:
                connection.privmsg(event.target(), functions.parseIRCBBCode("No PvE kills found"))
                connection.privmsg(event.target(), functions.parseIRCBBCode("[b]Syntax[/b]: %spve [time ago] [system]" % config["bot"]["prefix"]))

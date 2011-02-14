#!/usr/bin/python
#
# vim: filetype=python tabstop=4 expandtab:


import locale
import time

import users
import api

def parseParsable(parsable):
    if " AND " in parsable:
        systems = []
        for pot_sys in parsable.split(" AND "):
            systems += [pot_sys.replace(" IN ","").strip()]
    elif "," in parsable:
        systems = []
        for pot_sys in parsable.split(","):
            systems += [pot_sys.strip()]
    else:
        systems = [parsable]
    return systems

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
        
        #parse inputs
        try:
            inputs = " " + event.arguments()[0].split(" ", 1)[1]
        except IndexError:
            since = 0
            to = 2147483647
            systems = [None]
        else:
            #syntax:
            #     from DD/MM to DD/MM
            #     from DD/MM
            #     since DD/MM to DD/MM
            #     since/from DDst/nd/th (of Month/Mth) to DDst/nd/th (of Month/mth)
            #     DD/MM
            #     DDst/nd/th (of Month/Mth)
            #     DD/MM - DD/MM
            #     DDst/nd/th (of Month/Mth) - DDst/nd/th (of Month/Mth)
            
            if " FROM " in inputs or " SINCE " in inputs:
                if " FROM " in inputs:
                    separator = " FROM "
                else:
                    separator = " SINCE "
                #possibilities:
                # just from
                #1   from x
                # from and to
                #2   from x to x
                #3   to x from x
                # from and in
                #4   from x in x (and in x ...)
                #5   in x (and in x ...) from x
                # from and to and in
                #6   from x in x (and in x ...) to x
                #7   from x to x in x (and in x ...)
                #8   to x from x in x (and in x ...)
                #9   to x in x (and in x ...) from x
                #10  in x (and in x ...) to x from x
                #11  in x (and in x ...) from x to x
                if " TO " not in inputs and " IN " not in inputs:
                    #option 1
                    since = inputs.split(separator)[1].strip()
                    to = 2147483647
                    systems = [None]
                elif " TO " in inputs and " IN " not in inputs:
                    if inputs.index(separator) < inputs.index(" TO "):
                        #option 2
                        since = inputs.split(separator)[1].split(" TO ")[0].strip()
                        to = inputs.split(" TO ")[1].strip()
                        systems = [None]
                    else:
                        #option 3
                        since = inputs.split(separator)[1].strip()
                        to = inputs.split(" TO ")[1].split(separator)[0].strip()
                        systems = [None]
                elif " TO " not in inputs and " IN " in inputs:
                    if inputs.index(separator) < inputs.index(" IN "):
                        #option 4
                        systems = parseParsable(inputs.split(" IN ", 1)[1].strip())
                        since = inputs.split(separator)[1].split(" IN ")[0].strip()
                        to = 2147483647
                    else:
                        #option 5
                        systems = parseParsable(inputs.split(" IN ", 1)[1].split(separator)[0].strip())
                        since = inputs.split(separator)[1].strip()
                        to = 2147483647
                elif " TO " in inputs and " IN " in inputs:
                    #options 6-11
                    if inputs.index(separator) > inputs.index(" IN ") and inputs.index(" IN ") > inputs.index(" TO "):
                        #6   from x in x (and in x ...) to x
                        since = inputs.split(separator)[1].split(" IN ")[0].strip()
                        to = inputs.split(" TO ")[1].strip()
                        systems = parseParsable(inputs.split(" IN ",1)[1].split(" TO ")[0].strip())
                    elif inputs.index(separator) > inputs.index(" TO ") and inputs.index(" TO ") > inputs.index(" IN "):
                        #7   from x to x in x (and in x ...)
                        since = inputs.split(separator)[1].split(" TO ")[0].strip()
                        to = inputs.split(" TO ")[1].split(" IN ")[0].strip()
                        systems = parseParsable(inputs.split(" IN ", 1)[1])
                    elif inputs.index(" TO ") > inputs.index(separator) and inputs.index(separator) > inputs.index(" IN "):
                        #8   to x from x in x (and in x ...)
                        since = inputs.split(separator)[1].split(" IN ")[0].strip()
                        to = inputs.split(" TO ")[1].split(separator)[0].strip()
                        systems = parseParsable(inputs.split(" IN ", 1)[1].strip())
                    elif inputs.index(" TO ") > inputs.index(" IN ") and inputs.index(" IN ") > inputs.index(separator):
                        #9   to x in x (and in x ...) from x
                        since = inputs.split(separator)[1].strip()
                        to = inputs.split(" TO ")[1].split(" IN ")[0].strip()
                        systems = parseParsable(inputs.split(" IN ", 1)[1].split(" FROM ")[0].strip())
                    elif inputs.index(" IN ") > inputs.index(" TO ") and inputs.index(" TO ") > inputs.index(separator):
                        #10  in x (and in x ...) to x from x
                        since = inputs.split(separator)[1].strip()
                        to = inputs.split(" TO ")[1].split(separator)[0].strip()
                        systems = parseParsable(inputs.split(" IN ", 1)[1].split(" TO ")[0].strip())
                    else:
                        #11  in x (and in x ...) from x to x
                        since = inputs.split(separator)[1].split(" TO ")[0].strip()
                        to = inputs.split(" TO ")[1].strip()
                        systems = parseParsable(inputs.split(" IN ", 1)[1].split(" FROM ")[0].strip())
                        
                        
            elif "since" in inputs:
                if "to" in inputs:
                    since = inputs.split("since")[1].split("to")[0].strip()
            
            print "since:%s, to:%s, systems:%r" % (since, to, systems)
                
        
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
                    kills = walletdict[refID]["_kills_"]
                    for kill in kills:
                        if kill["shipName"] not in bounties.keys():
                            bounties[kill["shipName"]] = kill["count"]
                        else:
                            bounties[kill["shipName"]] += kill["count"]
                    total_bounty += walletdict[refID]["amount"]

                    bounty_date = walletdict[refID]["date"]
                    if bounty_date > latest_date:
                        latest_date = bounty_date
                    if bounty_date < earliest_date:
                        earliest_date = bounty_date

            bounties_list = sorted(bounties.items(), key=lambda ship: ship[1], reverse=True)
            connection.privmsg(event.target(), "\x02PvE stats for character \x038\x02\x02%s\x03 between %s and %s\x02" % (APItest["characterName"], time.asctime(time.gmtime(earliest_date)), time.asctime(time.gmtime(latest_date))))
            connection.privmsg(event.target(), "\x02Total bounty earned\x02: \x039\x02\x02%s ISK\x03\x02\x02" % locale.format("%.2f", total_bounty, True))
            if total_bounty != 0:
                connection.privmsg(event.target(), "\x02Top 5 NPC ships killed:\x02")
                for shiptype in bounties_list[:5]:
                    connection.privmsg(event.target(), "\x034\x02%-25s\x03\x02:  \x033\x02\x02%1i\x03" % (shiptype[0], shiptype[1]))

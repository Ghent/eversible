#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import locale
import time
import traceback

from modules import users
from modules import api
from modules.misc import functions


def index(connection, event, config):
    locale.setlocale(locale.LC_ALL, config["core"]["locale"])
    #requires limited api key

    #check identify
    USERS = users.DB()
    sourceHostName = event.source()
    sourceNick = event.source()

    response = USERS.retrieveUserByHostname(sourceHostName)
    if not response:
        connection.privmsg(event.target(), "This command requires your limited API key")
        connection.privmsg(event.target(), "Please identify or register in a private message")
    else:
        characterName = response["characterName"]
        characterID = response["characterID"]
        userID = response["userID"]
        apiKey = response["apiKey"]

        try:
            API = api.API(userid=userID, apikey=apiKey, charid=characterID)
            skillqueue = API.Char("skillqueue")
        except api.APIError:
            connection.privmsg(event.target(), "There was an error with the API: %s" % " ".join(traceback.format_exc().splitlines()[-1].split()[1:]))
        else:
            messages = ["\x02Skills currently in training for \x033\x02\x02%s\x03\x02:" % characterName]
            queuekeys = skillqueue.keys()
            queuekeys.sort()
            attributes = API.Char("charsheet")["attributes"]

            for i in queuekeys:
                if i == 8:
                    messages += ["\x02 + %i more\x02" % (len(queuekeys) - 8)]
                    break
                level = skillqueue[i]["level"]
                if level == 5:
                    level_roman = "V"
                elif level == 4:
                    level_roman = "IV"
                elif level == 3:
                    level_roman = "III"
                elif level == 2:
                    level_roman = "II"
                elif level == 1:
                    level_roman = "I"
                else:
                    level_roman = "?"

                typeName = skillqueue[i]["typeName"]

                needed_attributes = API.Eve("skilltree", typeID=skillqueue[i]["typeID"])

                startTime = skillqueue[i]["startTime"]
                endTime = skillqueue[i]["endTime"]

                startSP = skillqueue[i]["startSP"]
                endSP = skillqueue[i]["endSP"]

                SPtogo = endSP - startSP

                SPpersec = (float(attributes[needed_attributes["primaryAttribute"]]) + (float(attributes[needed_attributes["secondaryAttribute"]]) / 2)) / 60
                total_sec = SPtogo / SPpersec

                if i == 0:
                    secs_done = time.time() - startTime
                else:
                    secs_done = 0
                secs_to_go = total_sec - secs_done

                SPleft = endSP - (secs_done * SPpersec) - startSP
		print type(SPleft)

                messages += ["\x02%i\x02: \x1f%s %s\x1f \x02::\x02 %s SP to go \x02::\x02 Time to go: \x033\x02%s\x02\x03" %
                                   (i+1, typeName, level_roman, locale.format("%d", SPleft, True), functions.convert_to_human(secs_to_go))
                            ]
            for message in messages:
                connection.privmsg(event.target(), message)

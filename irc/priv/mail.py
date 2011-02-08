#!/usr/bin/env python

import users
import api
import time
import traceback
import re

def index(connection,event, config):
    #process search_from
    def process_search_from(search_from):
        #check all:
        idCheck = API.Eve("getid", nameName=search_from)
        if idCheck["ID"] == 0:
            #check for alliance ticker
            allianceInfo = API.Eve("alliances", allianceTicker=search_from)
            if allianceInfo:
                return {"alliance" : allianceInfo["allianceID"], "alliance" : allianceInfo["allianceTicker"]}
            #check for corp ticker <-- can't be implemented yet
        else:
            name = idCheck["Name"]
            id = idCheck["ID"]
        
            #check for alliance name
            allianceInfo = API.Eve("alliances", allianceID=id)
            if allianceInfo:
                return {"alliance" : allianceInfo["allianceID"], "allianceTicker" : allianceInfo["allianceTicker"]}
                
            #check for corp name
            corpInfo = API.Corporation("publicsheet", corporationID=id)
            if corpInfo:
                return {"corp" : corpInfo["corporationID"]}
                
            #check for char name
            charInfo = API.Eve("characterinfo", characterID=id)
            if charInfo:
                return {"char" : charInfo["characterID"]}
                            
    def convert_to_human(Time):
        mins, secs = divmod(Time, 60)
        hours, mins = divmod(mins, 60)
        days, hours = divmod(hours, 24)
        weeks, days = divmod(days, 7)
        
        time_str = ""
        if weeks > 0:
            time_str += "%iw " % weeks
        if days > 0:
            time_str += "%id " % days
        if hours > 0:
            time_str += "%ih " % hours
        if mins > 0:
            time_str += "%im " % mins
        if secs > 0:
            time_str += "%is" % secs
        return time_str
    
    USERS = users.DB()
    
    sourceHostName = event.source()
    sourceNick = event.source().split("!")[0]
    
    try:
        mailID = event.arguments()[0].split()[1]
        if "FROM:" in mailID.upper() or "TO:" in mailID.upper():
            mailID = None
        else:
            mailID = int(mailID)
    except IndexError:
        mailID = None
    except ValueError:
        if mailID.lower() == "help":
            connection.privmsg(sourceNick, "SYNTAX: mail (FROM:sender) (TO:recipient) (mail id)")
            return
        mailID = None
        

    
    try:
        args = " ".join(event.arguments()[0].split()[1:])
        search_from_partial = args.split("FROM:")[1]
        if "TO:" in search_from_partial and args.index("TO:") > args.index("FROM:"):
            search_from = search_from_partial.split("TO:")[0].strip()
        else:
            search_from = search_from_partial.strip()
    except IndexError:
        search_from = None
        
    try:
        args = " ".join(event.arguments()[0].split()[1:])
        search_to_partial = args.split("TO:")[1]
        if "FROM:" in search_to_partial and args.index("FROM:") > args.index("TO:"):
            search_to = search_to_partial.split("FROM:")[0].strip()
        else:
            search_to = search_to_partial.strip()
    except IndexError:
        search_to = None
    
    response = USERS.retrieveUserByHostname(sourceHostName)
    if not response:
        connection.privmsg(event.source().split("!")[0], "This command requires your full API key")
        connection.privmsg(event.source().split("!")[0], "Please identify or register")
    else:
        characterName = response["characterName"]
        characterID = response["characterID"]
        userID = response["userID"]
        apiKey = response["apiKey"]
        API = api.API(userid=userID, apikey=apiKey, charid=characterID)
        
        if not mailID:
            try:
                mailheaders = API.Char("mail")
            except api.APIError:
                connection.privmsg(sourceNick, "There was an error with the API: %s" % " ".join(traceback.format_exc().splitlines()[-1].split()[1:]))
            else:
                mailkeys = mailheaders.keys()
                mailkeys.sort()
                mailkeys.reverse()
                    
                wanted_recip_from = ""
                wanted_recip_to = ""
                
                title_string = "\x02Latest 5 mails\x02: "
                
                if search_from:
                    wanted_recip_from_dict = process_search_from(search_from)
                    if wanted_recip_from_dict:
                        if wanted_recip_from_dict.has_key("char"):
                            wanted_recip_from = wanted_recip_from_dict["char"]
                            wanted_recip_from_format = "\x034\x02\x02%s\x03\x02\x02" % search_from
                        elif wanted_recip_from_dict.has_key("alliance"):
                            wanted_recip_from = wanted_recip_from_dict["alliance"]
                            wanted_recip_from_format = "\x033\x02\x02%s\x03\x02\x02" % search_from
                        elif wanted_recip_from_dict.has_key("corp"):
                            wanted_recip_from = wanted_recip_from_dict["corp"]
                            wanted_recip_from_format = "\x037\x02\x02%s\x03\x02\x02" % search_from
                    else:
                        title_string += "( unknown sender %s ) " % search_from
                        search_from = None
                    
                        

                if search_to:
                    wanted_recip_to_dict = process_search_from(search_to)
                    if wanted_recip_to_dict:
                        if wanted_recip_to_dict.has_key("char"):
                            wanted_recip_to = wanted_recip_to_dict["char"]
                            wanted_recip_to_format = "\x034\x02\x02%s\x03\x02\x02" % search_to
                        elif wanted_recip_to_dict.has_key("alliance"):
                            wanted_recip_to = wanted_recip_to_dict["alliance"]
                            wanted_recip_to_format = "\x033\x02\x02%s\x03\x02\x02" % search_to
                        elif wanted_recip_to_dict.has_key("corp"):
                            wanted_recip_to = wanted_recip_to_dict["corp"]
                            wanted_recip_to_format = "\x037\x02\x02%s\x03\x02\x02" % search_to
                    else:
                        title_string += "( unknown recipient %s ) " % search_to
                        search_to = None

                mailkeys_temp = []
                for mailkey in mailkeys:
                    recipients = []
                    mail = mailheaders[mailkey]
                    if mail["allianceID"]:
                        recipients += [mail["allianceID"]]
                    #mail can be to both an alliance and a corp, so don't use elif here
                    if mail["corpID"]:
                        recipients += [mail["corpID"]]
                    if mail["toCharacters"]:
                        for id in mail["toCharacters"].keys():    
                            recipients += [id]
                    sender = mail["senderID"]
                    if search_from and not search_to:
                        if str(sender) == str(wanted_recip_from):
                            mailkeys_temp += [mailkey]
                    elif search_to and not search_from:
                        for recip in recipients:
                            if str(recip) == str(wanted_recip_to):
                                mailkeys_temp += [mailkey]
                    elif search_from and search_to:
                        if str(sender) == str(wanted_recip_from):
                            for recip in recipients:
                                if str(recip) == str(wanted_recip_to):
                                    mailkeys_temp += [mailkey]
                            
                mailkeys_temp.sort()
                mailkeys_temp.reverse()
                
                if mailkeys_temp != []:
                    if search_from and not search_to:
                        title_string += "from %s" % wanted_recip_from_format
                    elif search_to and not search_from:
                        title_string += "to %s" % wanted_recip_to_format
                    elif search_to and search_from:
                        title_string += "from %s \x02and\x02 to %s" % (wanted_recip_from_format, wanted_recip_to_format)
                        
                    first5 = mailkeys_temp[:5]
                else:
                    if search_from and not search_to:
                        title_string += "(no messages from %s) " % wanted_recip_from_format
                    elif search_to and not search_from:
                        title_string += "(no messages to %s)" % wanted_recip_to_format
                    elif search_to and search_from:
                        title_string += "(no messages both from %s and to %s)" % (wanted_recip_from_format, wanted_recip_to_format)
                    first5 = mailkeys[:5]
                    
                connection.privmsg(sourceNick, title_string)
                connection.privmsg(sourceNick, " (\x1f mail ID \x1f)")
                
                count = 1
                for header in first5:
                    title = mailheaders[header]["title"]
                    From = mailheaders[header]["senderName"]
                    To = []
                    if mailheaders[header]["allianceID"]:
                        To += ["\x033\x02\x02%s (\x02%s\x02)\x03" % (mailheaders[header]["allianceName"], mailheaders[header]["allianceTicker"])]
                    if mailheaders[header]["corpID"]:
                        To += ["\x037\x02\x02%s\x03" % mailheaders[header]["corpName"]]
                    if mailheaders[header]["toCharacters"]:
                        for charID, value in mailheaders[header]["toCharacters"].iteritems():
                            To += ["\x032\x02%s\x02\x03" % value["characterName"]]
                    TO = "\x02\x02,\x02\x02".join(To)
                    
                    timeSent = time.time() - mailheaders[header]["sentDate"]
                    human_time = convert_to_human(timeSent)
                    connection.privmsg(sourceNick, " (\x02%i\x02): \x1f%s\x1f from \x034\x02%s\x02\x03 to %s (%s ago)" % (header, title, From, TO, human_time))
                    count += 1
                
                connection.privmsg(sourceNick, "\x02Use syntax: \x02\x1f%smail [mail ID]\x1f\x02 to get the message body of a mail" % config["bot"]["prefix"])
        else:
            try:
                mailID = int(mailID)
                mailHeader = API.Char("mail")[mailID]
                message = API.Char("mail",mailID=mailID)
            except api.APIError:
                connection.privmsg(sourceNick, "There was an error with the API: %s" % " ".join(traceback.format_exc().splitlines()[-1].split()[1:]))
            except KeyError:
                connection.privmsg(sourceNick, "No such mail")
            else:
                title = mailHeader["title"]
                From = mailHeader["senderName"]
                To = []
                if mailHeader["allianceID"]:
                    To += ["\x033\x02\x02%s (\x02%s\x02)\x03" % (mailHeader["allianceName"], mailHeader["allianceTicker"])]
                if mailHeader["corpID"]:
                    To += ["\x037\x02\x02%s\x03" % mailHeader["corpName"]]
                if mailHeader["toCharacters"]:
                    for charID, value in mailHeader["toCharacters"].iteritems():
                        To += ["\x032\x02%s\x02\x03" % value["characterName"]]
                TO = "\x02\x02,\x02\x02".join(To)
                
                timeSent = time.time() - mailHeader["sentDate"]
                human_time = convert_to_human(timeSent)
                connection.privmsg(sourceNick, "(\x02%i\x02): \x1f%s\x1f from \x034\x02%s\x02\x03 to %s (%s ago)" % (mailID, title, From, TO, human_time))
                
                #parse out html                
                message = re.sub("(\<br\>)+", "\n", message)
                message = message.replace("<b>","\x02")
                message = message.replace("</b>","\x02")
                message = message.replace("<u>","\x1f")
                message = message.replace("</u>","\x1f")
                message = message.replace("&gt;",">").replace("&lt;","<")
                itemmatches = re.findall("(\<a href=\"showinfo:(\d+)\"\>(.*?)\<\/a\>)", message, re.DOTALL)
                for match in itemmatches:
                    html = match[0]
                    itemID = match[1]
                    itemName = match[2]
                    #message = message.replace(html, "\x1f%s\x1f ( http://games.chruker.dk/eve_online/item.php?type_id=%s )" % (itemName, itemID))
                    message = message.replace(html, "\x1f%s\x1f" % itemName)
                    
                itemmatches = re.findall("(\<a href=\"showinfo:5//(\d+)\"\>(.*?)\<\/a\>)", message, re.DOTALL)
                for match in itemmatches:
                    html = match[0]
                    solarSystemID = match[1]
                    solarSystemName = match[2]
                    message = message.replace(html, "\x035\x02%s\x03\x02" % solarSystemName)
                    
                itemmatches = re.findall("(\<a href=\"showinfo:4//(\d+)\"\>(.*?)\<\/a\>)", message, re.DOTALL)
                for match in itemmatches:
                    html = match[0]
                    ID = match[1]
                    Name = match[2]
                    message = message.replace(html, "\x0310\x02%s\x03\x02" % Name)
                    
                itemmatches = re.findall("(\<a href=\"showinfo:3//(\d+)\"\>(.*?)\<\/a\>)", message, re.DOTALL)
                for match in itemmatches:
                    html = match[0]
                    ID = match[1]
                    Name = match[2]
                    message = message.replace(html, "\x032\x02%s\x03\x02" % Name)
                    
                itemmatches = re.findall("(\<a href=\"showinfo:3//(\d+)\"\>(.*?)\<\/a\>)", message, re.DOTALL)
                for match in itemmatches:
                    html = match[0]
                    ID = match[1]
                    Name = match[2]
                    message = message.replace(html, "\x037\x02%s\x03\x02" % Name)
                    
                itemmatches = re.findall("(\<a href=\"showinfo:16159//(\d+)\"\>(.*?)\<\/a\>)", message, re.DOTALL)
                for match in itemmatches:
                    html = match[0]
                    ID = match[1]
                    Name = match[2]
                    message = message.replace(html, "\x033\x02%s\x03\x02" % Name)
                    
                itemmatches = re.findall("(\<a href=\"showinfo:1377//(\d+)\"\>(.*?)\<\/a\>)", message, re.DOTALL)
                for match in itemmatches:
                    html = match[0]
                    ID = match[1]
                    Name = match[2]
                    message = message.replace(html, "\x034\x02%s\x03\x02" % Name)
                    
                itemmatches = re.findall("(\<a href=\"showinfo:3867//(\d+)\"\>(.*?)\<\/a\>)", message, re.DOTALL)
                for match in itemmatches:
                    html = match[0]
                    ID = match[1]
                    Name = match[2]
                    message = message.replace(html, "\x02%s\x02" % Name)
                
                #remove all unparsed html tags
                message = re.sub("\<.*?\>","",message)
                
                for line in message.splitlines():
                    connection.privmsg(sourceNick, line)
                
                
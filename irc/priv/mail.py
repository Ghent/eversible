#!/usr/bin/env python

import users
import api
import time
import traceback

def index(connection,event):
    
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
        if "FROM" in mailID.upper() or "TO" in mailID.upper():
            mailID = None
        else:
            mailID = int(mailID)
    except IndexError:
        mailID = None
    except ValueError:
        mailID = None
        
    try:
        search_from = " ".join(event.arguments()[0].split()[1:]).upper().split("FROM:")[1].split()[0]
    except IndexError:
        search_from = None
        
    try:
        search_to = " ".join(event.arguments()[0].split()[1:]).upper().split("TO:")[1].split()[0]
    except IndexError:
        search_to = None
        
    print """
        mailID: %s
        search_from: %s
        search_to: %s
    """, (mailID, search_from, search_to)
        
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
                connection.privmsg(souceNick, "There was an error with the API: %s" % " ".join(traceback.format_exc().splitlines()[-1].split()[1:]))
            else:
                mailkeys = mailheaders.keys()
                mailkeys.sort()
                mailkeys.reverse()
                first5 = mailkeys[:5]
    
                connection.privmsg(sourceNick, "\x02Latest 5 mails\x02:")
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
                
                connection.privmsg(sourceNick, "\x02Use syntax: \x02\x1fmail [mail ID]\x1f\x02 to get the message body of a mail")
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
                
                #basic elements to parse into output:
                #- <br> -> \n
                #- <a href="showinfo:ItemID">Item Name</a> -> ItemName (link to item)
                #- <a href="showinfo:5//solarSystemID">solarSystemName</a> -> Name (link)
                #- <a " " " " " " " :4 -> constell
                #- <a               :3 -> region
                #- <a               :2 -> corp
                #- <a               :1377 -> char
                #- <a               :16159 -> alliance
                #- <a               :3867 -> station
                #- <b> -> bold
                #- </b> -> unbold
                
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
                
                
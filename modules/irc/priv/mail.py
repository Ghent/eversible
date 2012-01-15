#!/usr/bin/env python

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

from modules import api
import time
import traceback
import re
from modules.misc import functions
import cgi
from modules import users

def index(connection,event, config):
    sourceHostName = event.source()
    sourceNick = event.source().split("!")[0]
    
    USERS = users.DB()
    
    try:
        mailID = event.arguments()[0].split()[1]
        mailID = int(mailID)
    except (IndexError, ValueError):
        mailID = None

    response = USERS.retrieveUserByHostname(sourceHostName)
    if not response:
        connection.privmsg(event.source().split("!")[0], "This command requires your full API key")
        connection.privmsg(event.source().split("!")[0], "Please identify or register")
    else:
        characterName = response["characterName"]
        characterID = response["characterID"]
        API = response["apiObject"]
        
        if not mailID:
            try:
                connection.privmsg(sourceNick, "Fetching mail, please wait")
                mailheaders = API.Char("mail")
            except api.APIError:
                connection.privmsg(sourceNick, "There was an error with the API: %s" % " ".join(traceback.format_exc().splitlines()[-1].split()[1:]))
            else:
                #(309935139, {'listName': None, 'sentTime': 1326055740, 'title': 'Re: Re: Op: Big-badda-boom', 'toCharacterIDs':
                #'2081077519', 'senderID': 2081077519, 'listID': None, 'sentDate': '2012-01-08 20:49:00', 'messageID': 309935139,
                #'toCorpOrAlliance': '1102238026', 'senderName': 'Gheent'})
                sortedMail = sorted(mailheaders.items(), key=lambda x:x[1]["sentTime"], reverse=True)
                
                connection.privmsg(sourceNick, "\x02Latest 5 mails\x02:")
                connection.privmsg(sourceNick, " (\x1fmail ID\x1f)")
                for mail in sortedMail[:5]:
                    mailID = mail[0]
                    mailInfo = mail[1]
                    title = mailInfo["title"]
                    fromName = mailInfo["senderName"]
                    toIDs = mailInfo["toCharacterIDs"] + [mailInfo["toCorpOrAlliance"]]
                    toNameList = []
                    for ID in toIDs:
                        toName = API.Eve("getname", nameID=ID)
                        if toName:
                            toNameList += [toName["name"]]
                        else:
                            toNameList += [str(ID)]
                    to_formatted = functions.parseIRCBBCode("[colour=green][b]%s[/b][/colour]" % "[/b][/colour], [colour=green][b]".join(toNameList))
                    sentTime = mailInfo["sentTime"]
                    when = "%s ago" % (functions.convert_to_human(time.time() - sentTime))                    
                    message = functions.parseIRCBBCode(" ([b]%(mailID)s[/b]): [u]%(title)s[/u] from [colour=red]%(from)s[/colour] to %(to_formatted)s (%(when)s)" % {
                        "mailID" : mailID,
                        "title" : title,
                        "from" : fromName,
                        "to_formatted" : to_formatted,
                        "when" : when
                    })
                    connection.privmsg(sourceNick, message)
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
                if mailHeader["toCorpOrAlliance"]:
                    To += [functions.parseIRCBBCode("[colour=dark_green][b]%s[/b][/colour]" % API.Eve("getname", nameID=int(mailHeader["toCorpOrAlliance"]))["name"])]
                if mailHeader["toCharacterIDs"]:
                    for charID in mailHeader["toCharacterIDs"]:
                        To += [functions.parseIRCBBCode("[colour=blue][b]%s[/b][/colour]" % API.Eve("getname", nameID=charID))]
                TO = "\x02\x02,\x02\x02".join(To)
                
                timeSent = time.time() - mailHeader["sentTime"]
                
                ###############################################################################################
                
                human_time = functions.convert_to_human(timeSent)
                connection.privmsg(sourceNick, "(\x02%i\x02): \x1f%s\x1f from \x034\x02%s\x02\x03 to %s (%s ago)" % (mailID, title, From, TO, human_time))
                
                #parse out html                
                message = re.sub("(\<br\>)+", "\n", message)
                message = message.replace("<b>","\x02")
                message = message.replace("</b>","\x02")
                message = message.replace("<u>","\x1f")
                message = message.replace("</u>","\x1f")
                message = message.replace("&gt;",">").replace("&lt;","<").replace("&amp;", "&")
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
                
                

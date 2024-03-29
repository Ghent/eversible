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

# python modules
import calendar
import operator
import os
import random
import re
import sqlite3
import string
import sys
import time
import traceback
import urllib
import urllib2

# EVErsible modules
from modules import api
from modules import cache
from modules import rss
from modules import users
from modules.misc import functions
        
class Scheduler:
    def __init__(self):
        self.QUEUE = _QUEUE()
        self.USERS = users.DB()
        self.CACHE = cache.CACHE()
        self.RSS = rss.RSS()
        self.MAIL_RECORD = {}
        #char ID : {messageID: last mailID, sentTime : sent time}
                
    def start(self, refreshtime=300, connection=None, IRCconfig=None):
        self.connection = connection
        self.IRCconfig = IRCconfig
        while True:
            self.QUEUE.insert(self.checkAPIurls, None, time.time())
            if self.connection:
                self.QUEUE.insert(self.mailCheck, None, time.time())
                self.QUEUE.insert(self.RSS.checkFeeds, self.rssHandler, time.time())
            self.QUEUE.run()
            time.sleep(refreshtime)
        
    def rssHandler(self, feedDict):
        try:
            if feedDict:
                for feedName, results in feedDict.iteritems():
                    if results:
                        newcount = len(results)
                        keys = results.keys()
                        keys.sort()
                        keys.reverse()
                        if newcount > 2:
                            #use #eversible whilst testing
                            self.connection.privmsg(self.IRCconfig["irc"]["channel"], functions.parseIRCBBCode("There are [colour=green]%i[/colour] new items for feed: [b]%s[/b]" % (newcount, feedName)))
                        self.connection.privmsg(self.IRCconfig["irc"]["channel"], functions.parseIRCBBCode("%s: ([colour=yellow]%s ago[/colour]) [colour=light_green]%s[/colour] [ [colour=blue]%s[/colour] ]" % (feedName, functions.convert_to_human(time.time() - results[keys[0]]["date"]), results[keys[0]]["title"], results[keys[0]]["link"])))
        except:
            print "Error in scheduler thread (rssHandler):"
            traceback.print_exc()
            
    def mailCheck(self):
        #get identified users
        try:
            USERS = users.DB()
            loggedInHostnames = USERS.getHostnames()
            for id, hostname in loggedInHostnames.iteritems():
                API = None
                mailXML = None
                nick = hostname.split("!")[0]
                resp = USERS.retrieveUserByHostname(hostname)
                if resp:
                    API = resp["apiObject"]
                else:
                    print "No api object for id: %s, hostname: %s" % (id, hostname)
                    continue
                mails = API.Char("mail")
                
                ##############################################################
                if API.CHAR_ID in self.MAIL_RECORD.keys():
                    latest_time = self.MAIL_RECORD[API.CHAR_ID]["sentTime"]
                    latest_id = self.MAIL_RECORD[API.CHAR_ID]["messageID"]
                else:
                    result = USERS.getMessageID(API.CHAR_ID)
                    if result:
                        self.MAIL_RECORD[API.CHAR_ID] = {}
                        self.MAIL_RECORD[API.CHAR_ID]["sentTime"] = result[1]
                        self.MAIL_RECORD[API.CHAR_ID]["messageID"] = result[0]
                        latest_time = result[1]
                        latest_id = result[0]
                    else:
                        latest_time = None
                        latest_id = None                
                    
                new_latest_time = None
                new_latest_id = None
                
                newIDs = []
                count = 0
                
                mailList = sorted(mails.items(), key=lambda x: x[1]["sentTime"], reverse=True)
                for mailID, row in mailList:
#>>> mails.keys()
#['corpTicker', 'toCharacterIDs', 'listName', 'sentTime', 'title', 'corpID', 'allianceTicker', 'senderID', 'allianceID', 'listID', 'allianceName', 'sentDate', 'messageID', 'corpName', 'senderName']
                    messageID = row["messageID"]
                    sentDate = row["sentTime"]
                    if count <= 5:
                        count += 1
                    if count > 5:
                        break
                    
                    if sentDate > latest_time:
                        if sentDate > new_latest_time:
                            new_latest_time = sentDate
                            new_latest_id = messageID
                        newIDs += [messageID]
                if newIDs:
                    newIDs_len = len(newIDs)
                    self.connection.notice(nick, functions.parseIRCBBCode("You have [colour=red]%i[/colour] new mails" % newIDs_len))
                    
                    count = 0
                    ids = []
                    for i in range(5):
                        try:
                            ids += [str(newIDs[i])]
                            count += 1
                        except IndexError:
                            break
                    
                    if newIDs_len == count:
                        self.connection.notice(nick, functions.parseIRCBBCode("ids are: [b]%s[/b]" % ("[/b], [b]".join(ids))))
                    else:
                        self.connection.notice(nick, functions.parseIRCBBCode("First %i ids are: [b]%s[/b]" % (count, "[/b], [b]".join(ids))))
                        
                    #insert new data into users
                    USERS.insertMessageID(API.CHAR_ID, new_latest_id, new_latest_time)
                    self.MAIL_RECORD[API.CHAR_ID] = {
                        "messageID" : new_latest_id,
                        "sentTime" : new_latest_time
                    }
        except:
            print "Error in scheduler thread (mailCheck):"
            traceback.print_exc()
            
    def checkAPIurls(self):
        try:
            API = api.API()
            CACHE = cache.CACHE()
            tablenames = CACHE.getTableNames()
            
            conn = sqlite3.connect("var/cache/cache.db")
            cursor = conn.cursor()
            
            for tablename in tablenames:
                if tablename != "rss":
                    cursor.execute("""
                                   SELECT url, expireTime, requestName
                                   FROM %s
                                   """ % tablename)
                    rows = cursor.fetchall()
                    for url, expireTime, requestName in rows:
                        if time.time() > expireTime:
                            #remove old entry
                            CACHE.requestXML(url, postdata=None)
                            xml = urllib2.urlopen(url).read()
                            #check for error
                            try:
                                API._errorCheck(xml)
                            except api.APIError:
                                #this will prune out erroneous API calls from the cache
                                pass
                            else:
                                new_expireTime = API._getCachedUntil(xml)
                                CACHE.insertXML(url, requestName, xml, new_expireTime, postdata=None)
        except:
            print "Error in scheduler thread (checkAPIurls):"
            traceback.print_exc()
            
class _QUEUE:
    def __init__(self):
        self.QUEUE = {}        
    
    def insert(self, function, handler, run_time, *args, **kwargs):
        """
            Inserts a function into the queue
            
            handler must be a function that takes a single argument of the returned data from the inputed function
            
            e.g.
            >>> import time
            >>> def func(input):
            ...     print "func called!"
            ...     return input
                
            >>> def handler(returned):
            ...     print "handler called!"
            ...     print returned
                
            >>> s = QUEUE()
            >>> schedID = s.insert(func, handler, time.time(), "Hello World!")
            >>> s.run()
            func called!
            handler called!
            Hello World!
        """
        
        if not handler:
            def handler(arg):
                pass
            
        schedID = "".join([random.choice(string.digits + string.letters) for x in range(20)])
        self.QUEUE[schedID] = {
            "schedID" : schedID,
            "function" : function,
            "handler" : handler,
            "time" : run_time,
            "args" : args,
            "kwargs" : kwargs            
        }
        return schedID

        
    def remove(self, schedID):
        if schedID in self.QUEUE.keys():
            del self.QUEUE[schedID]
            return True
        else:
            return False
    
    def run(self):
        deleteIDs = []
        for item in self.QUEUE.items():
            schedID = item[0]
            if time.time() > item[1]["time"]:
                returned = item[1]["function"](*item[1]["args"], **item[1]["kwargs"])
                item[1]["handler"](returned)
                deleteIDs += [schedID]
        for delete in deleteIDs:
            self.remove(delete)

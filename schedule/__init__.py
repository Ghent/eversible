#!/usr/bin/env python

import time
import random
import string
import api
import cache
import sqlite3
import urllib
import urllib2
import sys
import users
import os
import calendar
import re
import rss
import traceback
from misc import functions
        
class Scheduler:
    def __init__(self):
        self.QUEUE = _QUEUE()
        self.USERS = users.DB()
        self.CACHE = cache.CACHE()
        self.RSS = rss.RSS()
        self.MAIL_RECORD = {}
        #char ID : {messageID: last mailID, sentTime : sent time}
                
    def start(self, refreshtime=300, connection=None, IRCconfig=None):
        try:
            self.connection = connection
            self.IRCconfig = IRCconfig
            while True:
                self.QUEUE.insert(self.checkAPIurls, None, time.time())
                if self.connection:
                    self.QUEUE.insert(self.mailCheck, None, time.time())
                    self.QUEUE.insert(self.RSS.checkFeeds, self.rssHandler, time.time())
                self.QUEUE.run()
                time.sleep(refreshtime)
        except:
            traceback.print_exc()
            raise TypeError
        
    def rssHandler(self, feedDict):
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
                    self.connection.privmsg(self.IRCconfig["irc"]["channel"], functions.parseIRCBBCode("%s: ([colour=grey]%s[/colour]) [colour=light_green]%s[/colour] [[colour=blue]%s[/colour]]" % (feedName, time.asctime(time.gmtime(results[keys[0]]["date"])), results[keys[0]]["title"], results[keys[0]]["link"])))
            
    def mailCheck(self):
        #get identified users
        loggedInHostnames = self.USERS.getHostnames()
        for id, hostname in loggedInHostnames.iteritems():
            API = None
            mailXML = None
            nick = hostname.split("!")[0]
            API = self.USERS.retrieveUserByHostname(hostname)["apiObject"]
            requesturl = os.path.join(API.API_URL, "char/MailMessages.xml.aspx")
            postdata = {
                "apiKey" : API.API_KEY,
                "userID" : API.USER_ID,
                "characterID" : API.CHAR_ID,
            }
            mailXML = self.CACHE.requestXML(requesturl, postdata, deleteOld=False)
            if not mailXML:
                mailXML = urllib2.urlopen(requesturl, urllib.urlencode(postdata)).read()
            
            
            if API.CHAR_ID in self.MAIL_RECORD.keys():
                latest_time = self.MAIL_RECORD[API.CHAR_ID]["sentTime"]
                latest_id = self.MAIL_RECORD[API.CHAR_ID]["messageID"]
            else:
                result = self.USERS.getMessageID(API.CHAR_ID)
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
            rows = re.finditer("\<row messageID=\"(?P<messageID>\d+)\" senderID=\"(?P<senderID>\d+)\" sentDate=\"(?P<sentDate>\d+-\d+-\d+ \d+:\d+:\d+)\" title=\"(?P<title>.*?)\" toCorpOrAllianceID=\"(?P<toCorpOrAllianceID>.*?)\" toCharacterIDs=\"(?P<toCharacterIDs>.*?)\" toListID=\"(?P<toListID>.*?)\" \/\>", mailXML)
            #cycle through
            count = 0
            while True:
                try:
                    row = rows.next().groupdict()
                except StopIteration:
                    break
                else:
                    messageID = int(row["messageID"])
                    sentDate = calendar.timegm(time.strptime(row["sentDate"], "%Y-%m-%d %H:%M:%S"))
                    if count < 5:
                        count += 1
                    
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
                self.USERS.insertMessageID(API.CHAR_ID, new_latest_id, new_latest_time)
                self.MAIL_RECORD[API.CHAR_ID] = {
                    "messageID" : new_latest_id,
                    "sentTime" : new_latest_time
                }
        
    def checkAPIurls(self):
        API = api.API()
        tablenames = self.CACHE.getTableNames()
        
        conn = sqlite3.connect("cache/cache.db")
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
                        self.CACHE.requestXML(url, postdata=None)
                        xml = urllib2.urlopen(url).read()
                        #check for error
                        try:
                            API._errorCheck(xml)
                        except api.APIError:
                            #this will prune out erroneous API calls from the cache
                            pass
                        else:
                            new_expireTime = API._getCachedUntil(xml)
                            self.CACHE.insertXML(url, requestName, xml, new_expireTime, postdata=None)
    
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

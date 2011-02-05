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
from misc import functions
class LOGGER:
    def __init__(self):
        self.LOGFILE = open("mail.log","a")
    def write(self, message):
        self.LOGFILE.write(message + "\n")
        self.LOGFILE.flush()
        #print "(%s) %s" % (time.asctime(), message)
    def shutdown(self):
        self.LOGFILE.flush()
        self.LOGFILE.close()
        
class Scheduler:
    def __init__(self):
        self.QUEUE = _QUEUE()
        self.USERS = users.DB()
        self.CACHE = cache.CACHE()
        
        self.MAIL_RECORD = {}
        #char ID : {messageID: last mailID, sentTime : sent time}
        
        self.LOG = LOGGER()
        
    def start(self, refreshtime=300, connection=None):
        while True:
            self.QUEUE.insert(self.checkAPIurls, None, time.time())
            if connection:
                self.QUEUE.insert(self.mailCheck, None, time.time(), connection)
            self.QUEUE.run()
            time.sleep(refreshtime)
        
    def mailCheck(self, connection):
        #get identified users
        loggedInHostnames = self.USERS.getHostnames()
        for id, hostname in loggedInHostnames.iteritems():
            API = None
            mailXML = None
            nick = hostname.split("!")[0]
            self.LOG.write("%s: Currently checking mail for %s (hostname: %s)" % (time.asctime().split()[3], nick, hostname))
            API = self.USERS.retrieveUserByHostname(hostname)["apiObject"]
            self.LOG.write("> Got API object")
            requesturl = os.path.join(API.API_URL, "char/MailMessages.xml.aspx")
            postdata = {
                "apiKey" : API.API_KEY,
                "userID" : API.USER_ID,
                "characterID" : API.CHAR_ID,
            }
            self.LOG.write("> Char ID: %s" % API.CHAR_ID)
            self.LOG.write("> Getting mail XML")
            self.LOG.write(">> Querying CACHE")
            mailXML = self.CACHE.requestXML(requesturl, postdata, deleteOld=False)
            if not mailXML:
                self.LOG.write(">> CACHE failed")
                self.LOG.write(">> Querying API")
                mailXML = urllib2.urlopen(requesturl, urllib.urlencode(postdata)).read()
                self.LOG.write(">> Inserting XML into CACHE")
                self.CACHE.insertXML(requesturl, "char", mailXML, API._getCachedUntil(mailXML), postdata)
            self.LOG.write(">> Got XML (%i lines)" % len(mailXML.split("\n")))
            
            
            self.LOG.write("> Checking if last mail recorded in memory")
            if API.CHAR_ID in self.MAIL_RECORD.keys():
                latest_time = self.MAIL_RECORD[API.CHAR_ID]["sentTime"]
                latest_id = self.MAIL_RECORD[API.CHAR_ID]["messageID"]
                self.LOG.write(">> Recorded! latest_time: %s, latest_id: %s" % (latest_time, latest_id))
            else:
                self.LOG.write(">> Not recorded! Checking user database")
                result = self.USERS.getMessageID(API.CHAR_ID)
                if result:
                    self.MAIL_RECORD[API.CHAR_ID] = {}
                    self.MAIL_RECORD[API.CHAR_ID]["sentTime"] = result[1]
                    self.MAIL_RECORD[API.CHAR_ID]["messageID"] = result[0]
                    latest_time = result[1]
                    latest_id = result[0]
                    self.LOG.write(">>> Stored in database! latest_time: %s, latest_id: %s" % (latest_time, latest_id))
                else:
                    self.LOG.write(">>> No record for this char, setting to None")
                    latest_time = None
                    latest_id = None                
                
            new_latest_time = None
            new_latest_id = None
            
            newIDs = []
            self.LOG.write("> Parsing XML")
            self.LOG.write(">> Cached Until: %s" % time.asctime(time.gmtime(API._getCachedUntil(mailXML))).split()[3])
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
                        self.LOG.write("> Mail id: %s, sentDate: %s, timediff: %s" % (messageID, sentDate, latest_time - sentDate))
                        count += 1
                    
                    if sentDate > latest_time:
                        if sentDate > new_latest_time:
                            new_latest_time = sentDate
                            new_latest_id = messageID
                        newIDs += [messageID]
                        self.LOG.write("> New mail! sentDate: %s, messageID: %s" % (sentDate, messageID))
            if newIDs:
                self.LOG.write("> There is definitely new mail -> reporting it")
                newIDs_len = len(newIDs)
                connection.notice(nick, functions.parseIRCBBCode("You have [colour=red]%i[/colour] new mails" % newIDs_len))
                
                count = 0
                ids = []
                for i in range(5):
                    try:
                        ids += [str(newIDs[i])]
                        count += 1
                    except IndexError:
                        break
                
                if newIDs_len == count:
                    connection.notice(nick, functions.parseIRCBBCode("ids are: [b]%s[/b]" % ("[/b], [b]".join(ids))))
                else:
                    connection.notice(nick, functions.parseIRCBBCode("First %i ids are: [b]%s[/b]" % (count, "[/b], [b]".join(ids))))
                    
                #insert new data into users
                self.LOG.write("> Inserting new data into user database")
                self.USERS.insertMessageID(API.CHAR_ID, new_latest_id, new_latest_time)
                self.LOG.write("> Adding new data to memory")
                self.MAIL_RECORD[API.CHAR_ID] = {
                    "messageID" : new_latest_id,
                    "sentTime" : new_latest_time
                }
            else:
                self.LOG.write("> No new mail")
            self.LOG.write(">>>>>> DONE <<<<<<<")
        
    def checkAPIurls(self):
        API = api.API()
        tablenames = self.CACHE.getTableNames()
        
        conn = sqlite3.connect("cache/cache.db")
        cursor = conn.cursor()
        
        for tablename in tablenames:
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
            >>> def func(input):
            ...     print "func called!"
            ...     return input
                
            >>> def handler(returned):
            ...     print "handler called!"
            ...     print returned
                
            >>> s = QUEUE()
            >>> schedID = s.insert(func, handler, "Hello World!")
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

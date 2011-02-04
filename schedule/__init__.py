#!/usr/bin/env python

import time
import random
import string
import api
import cache
import sqlite3
import urllib2
import sys

class Scheduler:
    def __init__(self):
        self.QUEUE = _QUEUE()
    
    def start(self, refreshtime=300, connection=None):
        while True:
            self.QUEUE.insert(self.checkAPIurls, None, time.time())
            if connection:
                self.QUEUE.insert(self.testIRC, self.testIRCHandler, time.time(), connection)
            self.QUEUE.run()
            time.sleep(refreshtime)
        
    def testIRC(self, connection):
        print "TESTING TESTING 1 2 3"
        return connection
    
    def testIRCHandler(self, connection):
        connection.privmsg("#eversible", "Test worked!")
        
    def checkAPIurls(self):
        ### DEBUG ###
        print "checkAPIurls called @ %s" % time.asctime().split()[3]
        lowest_expire = 999999999999
        lowest_value = ""
        lowest_table = ""
        ### END DEBUG ###
        CACHE = cache.CACHE()
        API = api.API()
        tablenames = CACHE.getTableNames()
        
        conn = sqlite3.connect("cache/cache.db")
        cursor = conn.cursor()
        
        for tablename in tablenames:
            cursor.execute("""
                           SELECT url, expireTime, requestName
                           FROM %s
                           """ % tablename)
            rows = cursor.fetchall()
            for url, expireTime, requestName in rows:
                ### DEBUG ###
                if expireTime < lowest_expire:
                    lowest_expire = expireTime
                    lowest_value = requestName
                    lowest_table = tablename
                ### END DEBUG ###
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
        ### DEBUG ###
        print "Next expire (%s/%s) in %ss (%s)" % (lowest_table, lowest_value, int(lowest_expire - time.time()), time.asctime(time.localtime(lowest_expire)).split()[3])
        ### END DEBUG ###
    
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

#!/usr/bin/env python

import sqlite3
import urllib
import time

class CACHE:
    def __init__(self):
        pass
        
    def insertXML(self, requesturl, xml, expireTime, postdata={}):
        conn = sqlite3.connect("cache/cache.db")
        self.cursor = conn.cursor()
        url = requesturl + "?" + urllib.urlencode(postdata)
        table = requesturl.split("/")[3]
        requestname = requesturl.split("/")[4].split(".")[0]
        
        try:
            self.cursor.execute("""
                            CREATE TABLE %s
                            (requestName text, url text, expireTime real, xml blob)
                            """ % (table)
                            )
        except sqlite3.OperationalError:
            pass
        
        binary_string = "".join(["%010s" % bin(ord(x)) for x in xml])
        self.cursor.execute("INSERT INTO %s (requestName, url, expireTime, xml) VALUES('%s', '%s', %f, '%s')" % (table, requestname, url, expireTime, binary_string))
        self.cursor.close()
        conn.close()
        
    def requestXML(self, requesturl, postdata={}):
        
        def shutdown(returnable):
            self.cursor.close()
            conn.close()
            return returnable
        conn = sqlite3.connect("cache/cache.db")
        self.cursor = conn.cursor()
        url = requesturl + "?" + urllib.urlencode(postdata)
        table = requesturl.split("/")[3]
        requestname = requesturl.split("/")[4].split(".")[0]
        try:
            self.cursor.execute("SELECT requestName, url, expireTime, xml FROM %s WHERE url='%s'" % (table, url))
        except sqlite3.OperationalError:
            shutdown(None)
        else:
            row = self.cursor.fetchone()
            if row:
                expireTime = row[2]
                if time.time() > expireTime:
                    #remove row
                    self.cursor.execute("""
                                        DELETE
                                        FROM %s
                                        WHERE url='%s'
                                        """ % (table, url)
                                       )
                    shutdown(None)
                else:
                    xml = "".join([chr(int(x,2)) for x in row[3].split()])
                    shutdown(xml)
        
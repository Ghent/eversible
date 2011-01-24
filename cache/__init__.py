#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


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
        
        self.cursor.execute("""
                            INSERT INTO %s
                            (requestName, url, expireTime, xml)
                            VALUES ("%s", "%s", %f, ?)
                            """ % (table, requestname, url, expireTime),
                            [buffer(xml)]
                            )
        conn.commit()
        self.cursor.close()
        conn.close()
        
    def requestXML(self, requesturl, postdata={}):
        
        def shutdown(returnable):
            conn.commit()
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
                print "Retrieved result, with expireTime: %s" % expireTime
                if time.time() > expireTime:
                    #remove row
                    self.cursor.execute("""
                                        DELETE
                                        FROM %s
                                        WHERE url='%s'
                                        """ % (table, url)
                                       )
                    conn.commit()
                    shutdown(None)
                else:
                    xml = str(row[3])
                    shutdown(xml)
        
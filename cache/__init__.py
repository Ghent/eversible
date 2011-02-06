#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import sqlite3
import urllib
import time

class CACHE:
    def __init__(self):
        pass
        
    def insertRSSDate(self, feedName, date):
        conn = sqlite3.connect("cache/cache.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           CREATE TABLE rss
                           (feedName text, date real)
                           """)
        except sqlite3.OperationalError:
            pass
        
        cursor.execute("""
                       DELETE FROM rss
                       WHERE feedName='%s'
                       """ % feedName)
        cursor.execute("""
                       INSERT INTO rss
                       (feedName, date)
                       VALUES ("%s","%s")
                       """ % (feedName, date))
        conn.commit()
        cursor.close()
        conn.close()
    def getRSSDate(self, feedName):
        conn = sqlite3.connect("cache/cache.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                        SELECT date
                        FROM rss
                        WHERE feedName='%s'
                        """ % feedName)
        except sqlite3.OperationalError:
            cursor.close()
            conn.close()
            return None
        else:
            row = cursor.fetchone()
            cursor.close()
            conn.close()
            if row:
                return float(row[0])
            else:
                return None
        
    def getTableNames(self):
        conn = sqlite3.connect("cache/cache.db")
        cursor = conn.cursor()
        cursor.execute("""
               SELECT name
               FROM sqlite_master
               WHERE type='table'
               ORDER BY name
               """)
        tablenames = [str(x[0]) for x in cursor.fetchall()]
        cursor.close()
        conn.close()
        return tablenames

    def insertXML(self, requesturl, Request, xml, expireTime, postdata={}):
        conn = sqlite3.connect("cache/cache.db")
        cursor = conn.cursor()
        if postdata:
            url = requesturl + "?" + urllib.urlencode(postdata)
        else:
            url = requesturl
        table = requesturl.split("/")[3]
        requestname = Request.lower()

        try:
            cursor.execute("""
                            CREATE TABLE %s
                            (requestName text, url text, expireTime real, xml blob)
                            """ % (table)
                            )
        except sqlite3.OperationalError:
            pass
        
        cursor.execute("""
                            INSERT INTO %s
                            (requestName, url, expireTime, xml)
                            VALUES ("%s", "%s", %f, ?)
                            """ % (table, requestname, url, expireTime),
                            [buffer(xml)]
                            )
        conn.commit()
        cursor.close()
        conn.close()
    
    def requestURLs(self, table, requestName):
        conn = sqlite3.connect("cache/cache.db")
        cursor = conn.cursor()
        cursor.execute("""
                       SELECT url
                       FROM %s
                       WHERE requestName='%s'
                       """ % (table.lower(), requestName.lower()))
        results = cursor.fetchall()
        if results:
            return [str(x[0]) for x in results]
        else:
            return None
    def requestXML(self, requesturl, postdata={}, deleteOld=True):
        def shutdown(returnable):
            conn.commit()
            cursor.close()
            conn.close()
            return returnable
        conn = sqlite3.connect("cache/cache.db")
        cursor = conn.cursor()
        if postdata:
            url = requesturl + "?" + urllib.urlencode(postdata)
        else:
            url = requesturl
        table = requesturl.split("/")[3]
        requestname = requesturl.split("/")[4].split(".")[0]
        try:
            cursor.execute("SELECT requestName, url, expireTime, xml FROM %s WHERE url='%s'" % (table, url))
        except sqlite3.OperationalError:
            shutdown(None)
        else:
            row = cursor.fetchone()
            if row:
                expireTime = row[2]
                if time.time() > expireTime and deleteOld:
                    #remove row
                    cursor.execute("""
                                        DELETE
                                        FROM %s
                                        WHERE url='%s'
                                        """ % (table, url)
                                       )
                    conn.commit()
                    shutdown(None)
                else:
                    xml = str(row[3])
                    cursor.close()
                    conn.close()
                    return xml
        
#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:

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

import sqlite3
import urllib
import time

class CACHE:
    def __init__(self):
        self.conn = sqlite3.connect("var/cache/cache.db", check_same_thread=False)
        self.cursor = self.conn.cursor()
        
    def insertRSS(self, feedName, url, date):
        try:
            self.cursor.execute("""
                           CREATE TABLE rss
                           (feedName text, url text, date real)
                           """)
        except sqlite3.OperationalError:
            pass
        
        self.cursor.execute("""
                       DELETE FROM rss
                       WHERE feedName= ?
                       """, (feedName,))
        self.cursor.execute("""
                       INSERT INTO rss
                       (feedName, url, date)
                       VALUES (?, ?, ?)
                       """, (feedName, url, date))
        self.conn.commit()
        
    def getRSS(self, feedName):
        try:
            self.cursor.execute("""
                        SELECT *
                        FROM rss
                        WHERE feedName= ?
                        """, (feedName,))
        except sqlite3.OperationalError:
            return (None, 0.0)
        else:
            row = self.cursor.fetchone()
            
            
            if row:
                return (row[1], float(row[2]))
            else:
                return (None, 0.0)
        
    def getTableNames(self):
        self.cursor.execute("""
               SELECT name
               FROM sqlite_master
               WHERE type='table'
               ORDER BY name
               """)
        tablenames = [str(x[0]) for x in self.cursor.fetchall()]
        return tablenames

    def insertXML(self, requesturl, Request, xml, expireTime, postdata={}):
        if postdata:
            url = requesturl + "?" + urllib.urlencode(postdata)
        else:
            url = requesturl
        table = requesturl.split("/")[3]
        requestname = Request.lower()

        try:
            self.cursor.execute("""
                            CREATE TABLE %s
                            (requestName text, url text, expireTime real, xml text)
                            """ % (table)
                            )
        except sqlite3.OperationalError:
            pass
        
        self.cursor.execute("""
                            INSERT OR ABORT INTO %s
                            (requestName, url, expireTime, xml)
                            VALUES (?, ?, ?, ?)
                        """ % (table), (requestname, url, expireTime, xml)
        )
        self.conn.commit()
    
    def requestURLs(self, table, requestName):
        self.cursor.execute("""
                       SELECT url
                       FROM %s
                       WHERE requestName=?
                       """ % (table.lower()), (requestName.lower(),))
        results = self.cursor.fetchall()
        if results:
            return [str(x[0]) for x in results]
        else:
            return None
        
    def requestXML(self, requesturl, postdata={}, deleteOld=True):
        def shutdown(returnable):
            self.conn.commit()
            return returnable
        if postdata:
            url = requesturl + "?" + urllib.urlencode(postdata)
        else:
            url = requesturl
        table = requesturl.split("/")[3]
        requestname = requesturl.split("/")[4].split(".")[0]
        try:
            self.cursor.execute("SELECT requestName, url, expireTime, xml FROM %s WHERE url=?" % (table), (url,))
        except sqlite3.OperationalError:
            shutdown(None)
        else:
            row = self.cursor.fetchone()
            if row:
                expireTime = row[2]
                if time.time() > expireTime and deleteOld:
                    #remove row
                    self.cursor.execute("""
                                        DELETE
                                        FROM %s
                                        WHERE url=?
                                        """ % (table), (url,)
                                       )
                    self.conn.commit()
                    shutdown(None)
                else:
                    xml = str(row[3])
                    return xml

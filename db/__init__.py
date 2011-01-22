#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import os
import urllib
import urllib2
import re
import collections
import sys
import time
import json
import sqlite3

class DUMP:
    def __init__(self):
        conn = sqlite3.connect("db/current.db")
        self.cursor = conn.cursor()

    def getItemNameByID(self, ID):
        self.cursor.execute("SELECT typeID,typeName FROM invTypes WHERE typeID='%s'" % ID)
        row = self.cursor.fetchone()
        if row:
            return row[1]
        else:
            return None

    def getItemIDByName(self, name):
        self.cursor.execute("SELECT typeID,typeName FROM invTypes WHERE typeName='%s'" % name)
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

    def getSystemNameByID(self, systemID):
        self.cursor.execute("SELECT solarSystemID,solarSystemName FROM mapSolarSystems WHERE solarSystemID='%s'" % systemID)
        row = self.cursor.fetchone()
        if row:
            return row[1]
        else:
            return None

    def getSystemIDByName(self, systemname):
        self.cursor.execute("SELECT solarSystemID,solarSystemName FROM mapSolarSystems WHERE solarSystemName LIKE '%s'" % systemname)
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None
        
    def getFactionNameByID(self, factionID):
        self.cursor.execute("SELECT factionID,factionName FROM chrFactions WHERE factionID='%s'" % factionID)
        row = self.cursor.fetchone()
        if row:
            return row[1]
        else:
            return None

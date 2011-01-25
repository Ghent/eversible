#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import os
import sys
import sqlite3

class DUMP:
    def __init__(self):
        conn = sqlite3.connect("db/current.db")
        self.cursor = conn.cursor()

    def getItemNameByID(self, ID):
        self.cursor.execute("""SELECT typeID,typeName
                            FROM invTypes
                            WHERE typeID='%s'
                            """ % ID)
        row = self.cursor.fetchone()
        if row:
            return row[1]
        else:
            return None

    def getItemIDByName(self, name):
        self.cursor.execute("""SELECT typeID,typeName
                            FROM invTypes
                            WHERE typeName LIKE '%s'
                            """ % name)
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

    def getSystemNameByID(self, systemID):
        self.cursor.execute("""
                            SELECT solarSystemID,solarSystemName
                            FROM mapSolarSystems
                            WHERE solarSystemID='%s'
                            """ % systemID)
        row = self.cursor.fetchone()
        if row:
            return row[1]
        else:
            return None

    def getSystemIDByName(self, systemname):
        self.cursor.execute("""
                            SELECT solarSystemID,solarSystemName
                            FROM mapSolarSystems
                            WHERE solarSystemName LIKE '%s'
                            """ % systemname)
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

    def getSystemName(self, systemname):
        self.cursor.execute("""
                            SELECT solarSystemID,solarSystemName
                            FROM mapSolarSystems
                            WHERE solarSystemName LIKE '%s'
                            """ % systemname)
        row = self.cursor.fetchone()
        if row:
            return row[1]
        else:
            return None

    def getConstellationNameByID(self, ID):
        self.cursor.execute("""
                            SELECT constellationID, constellationName
                            FROM mapConstellations
                            WHERE constellationID='%s'
                            """ % ID)
        row = self.cursor.fetchone()
        if row:
            return row[1]
        else:
            return None

    def getRegionNameByID(self, ID):
        self.cursor.execute("""
                            SELECT regionID, regionName
                            FROM mapRegions
                            WHERE regionID='%s'
                            """ % ID)
        row = self.cursor.fetchone()
        if row:
            return row[1]
        else:
            return None

    def getRegionName(self, regionname):
        self.cursor.execute("""
                            SELECT regionID, regionName
                            FROM mapRegions
                            WHERE regionName LIKE '%s'
                            """ % regionname)
        row = self.cursor.fetchone()
        if row:
            return row[1]
        else:
            return None

    def getRegionIDByName(self, regionname):
        self.cursor.execute("""
                            SELECT regionID, regionName
                            FROM mapRegions
                            WHERE regionName LIKE '%s'
                            """ % regionname)
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

    def getFactionNameByID(self, factionID):
        self.cursor.execute("""SELECT factionID,factionName
                            FROM chrFactions
                            WHERE factionID='%s'
                            """ % factionID)
        row = self.cursor.fetchone()
        if row:
            return row[1]
        else:
            return None

    def getSystemInfoByID(self, systemID):
        self.cursor.execute("""
                            SELECT solarSystemID,solarSystemName,security,securityClass,regionID,constellationID
                            FROM mapSolarSystems
                            WHERE solarSystemID='%s'
                            """ % systemID)
        row = self.cursor.fetchone()
        if row:
            return {
                "solarSystemID" : row[0],
                "solarSystemName" : row[1],
                "security" : row[2],
                "securityClass" : row[3],
                "regionID" : row[4],
                "regionName" : self.getRegionNameByID(row[4]),
                "constellationID" : row[5],
                "constellationName" : self.getConstellationNameByID(row[5])
            }
        else:
            return None

    def getSystemInfoByName(self, systemname):
        self.cursor.execute("""
                            SELECT solarSystemID,solarSystemName,security,securityClass,regionID,constellationID
                            FROM mapSolarSystems
                            WHERE solarSystemName LIKE '%s'
                            """ % systemname)
        row = self.cursor.fetchone()
        if row:
            return {
                "solarSystemID" : row[0],
                "solarSystemName" : row[1],
                "security" : row[2],
                "securityClass" : row[3],
                "regionID" : row[4],
                "regionName" : self.getRegionNameByID(row[4]),
                "constellationID" : row[5],
                "constellationName" : self.getConstellationNameByID(row[5])
            }
        else:
            return None

    def getMaterialsByTypeID(self, typeID):
        self.cursor.execute("""
                            SELECT typeID,materialTypeID,quantity
                            FROM invTypeMaterials
                            WHERE typeID='%s'
                            """ % typeID
                            )
        results = self.cursor.fetchall()
        materials = {}
        for result in results:
            materialName = self.getItemNameByID(result[1])
            quantity = result[2]
            materials[materialName] = quantity
        return materials

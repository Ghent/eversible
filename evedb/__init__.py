#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import os
import sys
import sqlite3

class DUMP:
    def __init__(self):
        conn = sqlite3.connect("evedb/current.db")
        self.cursor = conn.cursor()

    def getItemInfoByID(self, ID):
        #invTypes
        self.cursor.execute("""
                            SELECT *
                            FROM invTypes
                            WHERE typeID='%s'
                            """ % ID)
        row = self.cursor.fetchone()
        if not row:
            return None
        else:
            typeID,groupID,typeName,description,graphicID,radius,mass,volume,capacity,portionSize,raceID,basePrice,published,marketGroupID,chanceOfDuplicating,iconID = row
            return {
                "typeID" : int(typeID),
                "groupID" : int(groupID),
                "typeName" : typeName,
                "description" : description,
                "radius" : float(radius),
                "mass" : float(mass),
                "volume" : float(volume),
                "capacity" : float(capacity),
                "portionSize" : int(portionSize),
                "raceID" : int(raceID),
                "basePrice" : float(basePrice),
                "marketGroupID" : int(marketGroupID),
                "chanceOfDuplicating" : float(chanceOfDuplicating),   
            }

    def getTypeEffectsByID(self, typeID):
        self.cursor.execute("""
                            SELECT typeID, effectID, isDefault
                            FROM dgmTypeEffects
                            WHERE typeID='%s'
                            """ % typeID)
        results = []
        while True:
            try:
                row = self.cursor.next()
            except StopIteration:
                break
            else:
                if row[2] == 1:
                    isDefault = True
                else:
                    isDefault = False
                results += [{
                    "typeID" : int(row[0]),
                    "effectID" : int(row[1]),
                    "isDefault" : isDefault
                }]
                
        return results
            
        
    def getEffectByID(self, effectID):
        self.cursor.execute("""
                            SELECT *
                            FROM dgmEffects
                            WHERE effectID='%s'
                            """ % effectID)
        while True:
            try:
                row = self.cursor.next()
            except StopIteration:
                break
            else:
                return {
                    "effectID" : row[0],
                    "effectName" : row[1],
                    "effectCategory" : row[2],
                    "description" : row[5],
                    "isOffensive" : row[7],
                    "isAssistance" : row[8],
                    "durationAttribueID" : row[9],
                    "trackingSpeedAttributeID" : row[10],
                    "dischargeAttributeID" : row[11],
                    "rangeAttributeID" : row[12],
                    "falloffAttributeID" : row[13],
                    "displayName" : row[16],
                    "isWarpSafe" : row[17],
                    "rangeChance" : row[18],
                    "electronicChance" : row[19],
                    "propulsionChance" : row[20],
                    "npcUsageChanceAttributeID" : row[23],
                    "npcActivationChanceAttributeID" : row[24],
                    "fittingUsageChanceAttributeID" : row[25]
                }
    def getTypeAttributesByID(self, typeID):
        self.cursor.execute()
            #typeID ->
            #    dgmTypeEffects : typeID, effectID, isDefault
            #        effectID ->
            #            dgmEffects : effectID, effectName, effectCategory, description, isOffensive, isAssistance, durationAttributeID, trackingSpeedAttributeID, dischargeAttributeID, rangeAttributeID, falloffAttributeID, disallowAutoRepeat, displayName, isWarpSafe, rangeChance, electronicChance, propulsionChance, npcUsageChangeAttributeID, npcActivationChanceAttributeID, fittingUsageChanceAttributeID
            #            all .*?AttributeIDs feed into dgmAttributeTypes
            #    dgmTypeAttributes : typeID, attributeID, valueInt, valueFloat
            #        attributeID ->
            #            dgmAttributeTypes : attributeID, attributeName, defaultValue, displayName, unitID, stackable, highIsGood, categoryID
            #                unitID ->
            #                    eveUnits : unitID, unitName, displayName, description
            #                categoryID ->
            #                    dgmAttributeCategories : categoryID, categoryName, categoryDescription
            #    invMetaTypes : typeID, parentTypeID, metaGroupID
            #        parentTypeID -> feeds back into invTypes
            #        metaGroupID ->
            #           invMetaGroups : metaGroupID, metaGroupName, description
            #            
            #groupID ->
            #    invGroups : groupID, groupName, categoryID, description, useBasePrice, allowManufacture, allowRecycler, anchored, anchorable, fittableNonSingleton
            #        categoryID ->
            #            invCategories : categoryID, categoryName, description
            #raceID ->
            #    chrRaces : raceID, raceName, description, shortDescription
            #marketGroupID ->
            #    invMarketGroups : marketGroupID, parentGroupID, marketGroupName, hasTypes
            #    parentGroupID feeds back
            
            
        #
#typeID|groupID|typeName|description|graphicID|radius|mass|volume|capacity|portionSize|raceID|basePrice|published|marketGroupID|chanceOfDuplicating|iconID
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

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

import os
import sys
import sqlite3
import urllib
import urllib2
import re
import bz2
import shutil

from modules.misc import progressbar

def testEveDB():
    try:
        EVEDB = DUMP()
        EVEDB.getSystemIDByName("Jita")
    except (sqlite3.OperationalError, sqlite3.DatabaseError):
        currentLink = os.readlink("var/eve/current.db")
        currentDB = os.path.dirname(currentLink)
        currentFile = os.path.basename(currentLink)
        print "Your static database is invalid or not up to date"
        fetch = raw_input("Would you like EVErsible to attempt to download a new version for you? [N]: ")
        if fetch.upper() == "YES" or fetch.upper() == "Y":
            EVEDB._getDatabase(currentDB, currentFile)
            return False
        else:
            return False
    else:
        return True

class DUMP:
    def __init__(self):
        try:
            conn = sqlite3.connect("var/eve/current.db")
            self.cursor = conn.cursor()
        except sqlite3.OperationalError:
            currentLink = os.readlink("var/eve/current.db")
            currentDB = os.path.dirname(currentLink)
            currentFile = os.path.basename(currentLink)
            print "The EVE database is missing"
            fetch = raw_input("Would you like EVErsible to attempt to download it for you? [N]: ")
            if fetch.upper() == "YES" or fetch.upper() == "Y":
                self._getDatabase(currentDB, currentFile)
            else:
                print "Not downloading, exiting..."
            sys.exit(0)
            
    def _getDatabase(self, currentDB, targetFile):
        
        def srchZofu():
            SRC_URI = "http://zofu.no-ip.de/"
            print "Searching http://zofu.no-ip.de"
            SRC_FILES = re.findall("<li>.*? <a href=\"(.*?)\/\">(.*?)<\/a><\/li>", urllib2.urlopen(SRC_URI).read())
            for src_file in SRC_FILES:
                if src_file[0] == src_file[1] and src_file[0] == currentDB:
                    print "Found correct release %s" % src_file[0]
                    SRC_FILE_URI = "%s%s" % (SRC_URI, src_file[1])
                    SQLITE_FILES = re.findall("<a href=\"(.*?)\">%s-sqlite3-v(\d+).*?<\/a>" % (currentDB), urllib2.urlopen(SRC_FILE_URI).read())
                    SQLITE_FILE_HREF = None
                    SQLITE_FILE_VERSION = 0
                    try:
                        for sqlite_file_href, sqlite_file_version in SQLITE_FILES:
                            if int(sqlite_file_version) > SQLITE_FILE_VERSION:
                                SQLITE_FILE_HREF = sqlite_file_href
                                SQLITE_FILE_VERSION = sqlite_file_version
                    except:
                        pass
                    if not SQLITE_FILE_HREF:
                        return (None, None)
                    
                    SQLITE_FILE_URI = "%s/%s" % (SRC_FILE_URI, SQLITE_FILE_HREF)
                    return (SQLITE_FILE_URI, SQLITE_FILE_HREF)
            return (None, None)
        def srchMP():
            SRC_URI = "https://mountainpenguin.org.uk/evedb"
            print "Searching mountainpenguin.org.uk"
            SRC_FILES = re.findall("<tr><td class=\"n\"><a href=\"(.*?)\">(.*?)-sqlite3.*?</a>", urllib2.urlopen(SRC_URI).read())
            SQLITE_FILE_HREF = None
            SQLITE_FILE_VERSION = 0
            try:
                for sqlite_file_href, sqlite_file_name in SRC_FILES:
                    if sqlite_file_name == currentDB:
                        SQLITE_FILE_HREF = sqlite_file_href
                        break
            except:
                pass
            
            if not SQLITE_FILE_HREF:
                return (None, None)
            
            SQLITE_FILE_URI = "%s/%s" % (SRC_URI, SQLITE_FILE_HREF)
            return (SQLITE_FILE_URI, SQLITE_FILE_HREF)
            #<tr><td class="n"><a href="cruc101-sqlite3-v1.db.bz2">cruc101-sqlite3-v1.db.bz2</a></td><td class="m">2011-Dec-06 15:47:01</td><td class="s">76.0M</td><td class="t">application/x-bzip</td></tr>
                    
        SQLITE_FILE_URI, SQLITE_FILE_HREF = srchMP()
        if not SQLITE_FILE_URI:
            print "Couldn't find release on mountainpenguin.org.uk"
            SQLITE_FILE_URI, SQLITE_FILE_HREF = srchZofu()
        if not SQLITE_FILE_URI:
            print "Couldn't find release on zofu.no-ip.de"
            print "Exiting..."
            sys.exit()
        else:
        ###debug###
        #if True:
        #    if True:
        #        SQLITE_FILE_URI = "https://mountainpenguin.org.uk/~irc/inc15-sqlite3-v1.db.bz2"
        #        SQLITE_FILE_HREF = "inc15-sqlite3-v1.db.bz2"
        ###enddebug###
                SQLITE_URLFILE = urllib2.urlopen(SQLITE_FILE_URI)
                SQLITE_FILE_LENGTH = int(SQLITE_URLFILE.info().get("Content-Length"))
                print "Downloading", SQLITE_FILE_URI
                SQLITE_FILE_SIZE = self._convert_size_to_human(SQLITE_FILE_LENGTH)
                
                #start downloading
                chunksize = 1024
                if not os.path.exists("var/eve/temp"):
                    print "Creating temporary directory var/eve/temp"
                    os.mkdir("var/eve/temp")
                TEMP_PATH = os.path.join("var/eve/temp", SQLITE_FILE_HREF)
                if os.path.exists(TEMP_PATH):
                    print "Temporary file %s already exists, removing ..." % TEMP_PATH
                    os.remove(TEMP_PATH)
                    
                OUTPUT_FILE = open(TEMP_PATH, "ab")
                
                class DLWidget(progressbar.ProgressBarWidget):
                    def update(self, pbar):
                        return "%s / %s" % (self._convert_size_to_human(pbar.currval).rjust(len(self._convert_size_to_human(pbar.maxval))), self._convert_size_to_human(pbar.maxval).rjust(len(self._convert_size_to_human(pbar.maxval))))
                        
                    def _convert_size_to_human(self, SIZE_BYTES):
                       if SIZE_BYTES >= 1024*1024*1024:
                           #gb
                           return "%.02f GiB" % (float(SIZE_BYTES)/1024**3)
                       elif SIZE_BYTES >= 1024*1024:
                           #mb
                           return "%.02f MiB" % (float(SIZE_BYTES)/1024**2)
                       elif SIZE_BYTES >= 1024:
                           return "%.02f KiB" % (float(SIZE_BYTES)/1024)
                       else:
                           return "%i B" % SIZE_BYTES
                        
                P_WIDGETS = [
                    DLWidget(), " ", progressbar.Percentage(), " ", progressbar.Bar(marker="=",left="[", right="]"),
                    " ", progressbar.ETA(), " ", progressbar.FileTransferSpeed()
                ]
                P = progressbar.ProgressBar(widgets=P_WIDGETS, maxval=SQLITE_FILE_LENGTH).start()
                progress = 0
                
                while True:
                    data = SQLITE_URLFILE.read(chunksize)
                    if not data:
                        P.finish()
                        OUTPUT_FILE.flush()
                        OUTPUT_FILE.close()
                        break
                    OUTPUT_FILE.write(data)
                    progress += len(data)
                    P.update(progress)
                
                TARGET_DIR = os.path.dirname(os.path.join("var/eve/", os.readlink("var/eve/current.db")))
                if not os.path.exists(TARGET_DIR):
                    os.mkdir(TARGET_DIR)
                    
                print "Extracting file"
                BZFILE = open(TEMP_PATH, "rb")
                if os.path.exists(os.path.join(TARGET_DIR, targetFile)):
                    print "Target file %s already exists, removing ..." % os.path.join(TARGET_DIR, targetFile)
                    os.remove(os.path.join(TARGET_DIR, targetFile))
                TARGET_FILE = open(os.path.join(TARGET_DIR, targetFile), "ab")
                chunksize = 4096
                read = 0
                uncomp = 0
                D = bz2.BZ2Decompressor()
                
                class DL2Widget(DLWidget):
                    def update(self, pbar):
                        return "%s" % self._convert_size_to_human(pbar.currval).rjust(len(self._convert_size_to_human(pbar.maxval)))
                class WrittenWidget(DLWidget):
                    def update(self, pbar):
                        return self._convert_size_to_human(uncomp)
                        
                P_WIDGETS = [
                    DL2Widget(), " --> ", WrittenWidget(), " ", progressbar.Percentage(), " ", progressbar.Bar(marker="-",left="[", right="]"),
                    " ", progressbar.ETA(), " ", progressbar.FileTransferSpeed()
                ]

                P = progressbar.ProgressBar(widgets=P_WIDGETS, maxval=SQLITE_FILE_LENGTH).start()
                while True:
                    compr_data = BZFILE.read(chunksize)
                    if not compr_data:
                        P.finish()
                        TARGET_FILE.flush()
                        TARGET_FILE.close()
                        break
                    read += len(compr_data)
                    P.update(read)
                    data = D.decompress(compr_data)
                    uncomp += len(data)
                    TARGET_FILE.write(data)
                
                print "Cleaning up"
                print "Removing var/eve/temp"
                shutil.rmtree("var/eve/temp")
                print "All Done"
                
                
                
    def _convert_size_to_human(self, SIZE_BYTES):
       if SIZE_BYTES >= 1024*1024*1024:
           #gb
           return "%.02f GiB" % (float(SIZE_BYTES)/1024**3)
       elif SIZE_BYTES >= 1024*1024:
           #mb
           return "%.02f MiB" % (float(SIZE_BYTES)/1024**2)
       elif SIZE_BYTES >= 1024:
           return "%.02f KiB" % (float(SIZE_BYTES)/1024)
       else:
           return "%i B" % SIZE_BYTES
                
                
    def _download(self, url):
        pass

    def getItemInfoByID(self, ID):
        #invTypes
        self.cursor.execute("""
                            SELECT *
                            FROM invTypes
                            WHERE typeID=?
                            """, (ID,))
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
                            WHERE typeID=?
                            """, (typeID,))
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
                            WHERE effectID=?
                            """, (effectID,))
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
        return
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
                            WHERE typeID=?
                            """, (ID,))
        row = self.cursor.fetchone()
        if row:
            return row[1]
        else:
            return None

    def getItemIDByName(self, name):
        self.cursor.execute("""SELECT typeID,typeName
                            FROM invTypes
                            WHERE typeName LIKE ?
                            """, (name,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

    def getSystemNameByID(self, systemID):
        self.cursor.execute("""
                            SELECT solarSystemID,solarSystemName
                            FROM mapSolarSystems
                            WHERE solarSystemID=?
                            """, (systemID,))
        row = self.cursor.fetchone()
        if row:
            return row[1]
        else:
            return None

    def getSystemIDByName(self, systemname):
        self.cursor.execute("""
                            SELECT solarSystemID,solarSystemName
                            FROM mapSolarSystems
                            WHERE solarSystemName LIKE ?
                            """, (systemname,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

    def getSystemName(self, systemname):
        self.cursor.execute("""
                            SELECT solarSystemID,solarSystemName
                            FROM mapSolarSystems
                            WHERE solarSystemName LIKE ?
                            """, (systemname,))
        row = self.cursor.fetchone()
        if row:
            return row[1]
        else:
            return None

    def getConstellationNameByID(self, ID):
        self.cursor.execute("""
                            SELECT constellationID, constellationName
                            FROM mapConstellations
                            WHERE constellationID=?
                            """, (ID,))
        row = self.cursor.fetchone()
        if row:
            return row[1]
        else:
            return None

    def getRegionNameByID(self, ID):
        self.cursor.execute("""
                            SELECT regionID, regionName
                            FROM mapRegions
                            WHERE regionID=?
                            """, (ID,))
        row = self.cursor.fetchone()
        if row:
            return row[1]
        else:
            return None

    def getRegionName(self, regionname):
        self.cursor.execute("""
                            SELECT regionID, regionName
                            FROM mapRegions
                            WHERE regionName LIKE ?
                            """, (regionname,))
        row = self.cursor.fetchone()
        if row:
            return row[1]
        else:
            return None

    def getRegionIDByName(self, regionname):
        self.cursor.execute("""
                            SELECT regionID, regionName
                            FROM mapRegions
                            WHERE regionName LIKE ?
                            """, (regionname,))
        row = self.cursor.fetchone()
        if row:
            return row[0]
        else:
            return None

    def getFactionNameByID(self, factionID):
        self.cursor.execute("""SELECT factionID,factionName
                            FROM chrFactions
                            WHERE factionID=?
                            """, (factionID,))
        row = self.cursor.fetchone()
        if row:
            return row[1]
        else:
            return None

    def getSystemInfoByID(self, systemID):
        self.cursor.execute("""
                            SELECT solarSystemID,solarSystemName,security,securityClass,regionID,constellationID
                            FROM mapSolarSystems
                            WHERE solarSystemID=?
                            """, (systemID,))
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
                            WHERE solarSystemName LIKE ?
                            """, (systemname,))
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
                            WHERE typeID=?
                            """, (typeID,)
                            )
        results = self.cursor.fetchall()
        materials = {}
        for result in results:
            materialName = self.getItemNameByID(result[1])
            quantity = result[2]
            materials[materialName] = quantity
        return materials

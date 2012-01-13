#!/usr/bin/env python
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

    Container for the API and APIError classes
"""
# vim: filetype=python tabstop=4 expandtab:


import os
import urllib
import urllib2
import re
import collections
import sys
import time
from modules import evedb
from modules import cache
import calendar
import traceback
from xml.etree import ElementTree as etree
import cStringIO as StringIO
from modules.misc import functions

class DictToObject:
    # copied from Eli Bendersky on stackoverflow
    # <http://stackoverflow.com/questions/1305532/convert-python-dict-to-object>
    def __init__(self, **entries):
        self.__dict__.update(entries)
        
class APIError(Exception):
    def __init__(self, code, value):
        self.code = int(code)
        self.value = value
    def __str__(self):
        return repr((self.code, self.value))

class API:
    """
        Wrapper for API requests
    """
    def __init__(self, keyID=None, vCode=None, charid=None, characterName=None, debug=False):
        """
            If no arguments are specified, functions that require no API information will still be functional
            
            Keyword arguments:
            -------------------------------------------------------------------------------------------
              keyID         -- API key ID (defaults to None)
              vCode         -- the verification code associated with keyID (defaults to None)
              charid        -- the character ID, can be omitted if not known (defaults to None)
              characterName -- if charid is not specified, characterName should be (defaults to None)
              debug         -- defaults to False, this argument is deprecated and does nothing
            --------------------------------------------------------------------------------------------
            all arguments are optional
        """
        if not keyID or not vCode:
            raise APIError(0, "keyID and/or vCode not specified")
        if not charid and not characterName:
            raise APIError(1, "Character not specified")
        self.KEY_ID = self.keyID = keyID
        self.V_CODE = self.vCode = vCode
        self.API_URL = "http://api.eve-online.com"
        self.DEBUG = debug
        self.EVE = evedb.DUMP()
        self.CACHE = cache.CACHE()
        if not charid and characterName:
            #get CHAR_ID from API
            chardict = self.Account("characters")
            if chardict and characterName in chardict.keys():
                self.CHAR_ID = chardict[characterName]["characterID"]
        else:
            self.CHAR_ID = int(charid)
        
    def _convertEveToUnix(self, timestamp):
        try:
            return calendar.timegm(time.strptime(timestamp, "%Y-%m-%d %H:%M:%S"))
        except:
            return None
    def _getXML(self, requesturl, Request, postdata={}, permanent=False, raw=False):
        """
            Request XML for a given URL, associated with POST data
            
            Keyword arguments:
            -------------------------------------------------------------------
            * requesturl -- the base URL of a particular API request
            * Request    -- the Request
              postdata   -- a dictionary object containing POST keys / values
            -------------------------------------------------------------------
            * = required
            
            Returns: ElementTree object
        """
        xml = self.CACHE.requestXML(requesturl, postdata)
        if not xml:
            xml = urllib2.urlopen(requesturl, urllib.urlencode(postdata)).read()
            if not permanent:
                self.CACHE.insertXML(requesturl, Request, xml, self._getCachedUntil(xml), postdata)
            else:
                self.CACHE.insertXML(requesturl, Request, xml, 2147483647.0, postdata)
        if raw:
            return xml
        xmltree = etree.parse(StringIO.StringIO(xml))
        self._errorCheck(xmltree)
        return xmltree
        
    def _errorCheck(self, xmltree):
        """
            Parses errors from API returned XML and raises an appropriate APIError
            
            Keyword arguments:
            ------------------------------------------
            * xmltree  -- the parsed XML returned by an API call
            ------------------------------------------
            * = required
        """
        if xmltree.find("error") is not None:
            error = xmltree.find("error")
            raise APIError(error.attrib["code"], error.text)
        
    def _getCachedUntil(self, xmltree):
        """
            Parses the <cachedUntil> value from the XML returned from an API call
            
            Keyword arguments:
            ------------------------------------------
            * xmltree  -- the parsed XML returned by an API call
            ------------------------------------------
            * = required
        """
        if type(xmltree) != etree.ElementTree:
            xmltree = etree.parse(StringIO.StringIO(xmltree))
        cachedUntil = self._convertEveToUnix(xmltree.find("cachedUntil").text)
        return cachedUntil
    
    def Eve(self,Request, allianceID=None, nameID=None, nameName=None, allianceName=None, allianceTicker=None, characterID=None, typeID=None):
        """
            Methods for retrieving EVE related data
            
            (NOTE: all times and dates are returned as floats representing the seconds since the start of the unix epoch)
            
            Keyword arguments:
            ----------------------------------------------------------------------------------------
            * Request        -- the particular request (see below)
              allianceID     -- alliance ID (used in alliances)
              nameID         -- generic for any character, corporation or alliance ID (used in getName)
              nameName       -- generic for any character, corporation or alliance name (used in getID)
              allianceName   -- the name of an alliance (used in alliances)
              allianceTicker -- the ticker of an alliance (used in alliances)
              characterID    -- the ID of a character (used in characterinfo)
              typeID         -- the ID of a skill type (used in skillTree)
            ----------------------------------------------------------------------------------------
            * = required
            
            Request:
            +--------------------------------------------------------------------------------------+
            | (N) alliances                                                                        |
            | description : returns alliance info for a given alliance ID, name or ticker          |
            | inputs      : allianceID, allianceName or allianceTicker                             |
            | returns     : dict with keys allianceID, allianceName, allianceTicker, startDate,    |
            |               startTime (unix timestamp), memberCount, and executorCorpID            |
            +--------------------------------------------------------------------------------------+
            | (N) getName                                                                          |
            | description : returns the name for a given character, corp or alliance ID            |
            | inputs      : nameID*                                                                |
            | returns     : dict with keys name and ID                                             |
            +--------------------------------------------------------------------------------------+
            | (N) getID                                                                            |
            | description : returns the ID for a given character, corp or alliance name            |
            | inputs      : nameName*                                                              |
            | returns     : dict with keys name and ID                                             |
            +--------------------------------------------------------------------------------------+
            | (N) characterinfo                                                                    |
            | description : returns the public info for a given character ID                       |
            | inputs      : characterID*                                                           |
            | returns     : dict with keys characterID, characterName, race, bloodline,            |
            |               corporationID, corporationName, corporationDate, allianceID,           |
            |               allianceName, allianceDate, securityStatus                             |
            +--------------------------------------------------------------------------------------+
            | (N) reftypes                                                                         |
            | description : returns the refTypes with associated names as used in the wallet       |
            |               journal, the returned XML will be cached essentially for ever          |
            | inputs      : none                                                                   |
            | returns     : dict with key refTypeID (int) and value refTypeName                    |  
            +--------------------------------------------------------------------------------------+
            | (N) skillTree                                                                        |
            | description : returns limited information about a particular skill                   |
            | inputs      : none                                                                   | 
            | returns     : dict with keys typeID                                                  |
            +--------------------------------------------------------------------------------------+
            (N) = No API key required
             *  = required input
        """
        if Request.lower() == "alliances":
            requesturl = os.path.join(self.API_URL, "eve/AllianceList.xml.aspx")
            xmltree = self._getXML(requesturl, Request)
            allianceList = xmltree.findall("result/rowset/row")
            result = False
            if allianceID:
                #{'startDate': '2010-06-01 05:36:00', 'name': 'Goonswarm Federation', 'allianceID': '1354830081',
                # 'memberCount': '7272', 'shortName': 'CONDI', 'executorCorpID': '667531913'}
                for allianceRow in allianceList:
                    if str(allianceID) == allianceRow.attrib["allianceID"]:
                        result = allianceRow
                        break
            elif allianceName:
                for allianceRow in allianceList:
                    if allianceName == allianceRow.attrib["name"]:
                        result = allianceRow
                        break
            elif allianceTicker:
                for allianceRow in allianceList:
                    if allianceTicker == allianceRow.attrib["shortName"]:
                        result = allianceRow
                        break

            if result is not False:
                allianceID = result.attrib["allianceID"]
                allianceName = result.attrib["name"]
                allianceTicker = result.attrib["shortName"]
                startDate = result.attrib["startDate"]
                startTime = self._convertEveToUnix(startDate)
                memberCount = result.attrib["memberCount"]
                executorCorpID = result.attrib["executorCorpID"]
                return {
                    "allianceID" : int(allianceID),
                    "allianceName" : allianceName,
                    "allianceTicker" : allianceTicker,
                    "startDate" : startDate,
                    "startTime" : startTime,
                    "memberCount" : int(memberCount),
                    "executorCorpID" : int(executorCorpID)
                }
                
        elif Request.lower() == "getname":
            requesturl = os.path.join(self.API_URL, "eve/CharacterName.xml.aspx")
            if nameID:
                postdata = {
                    "ids" : nameID
                }
                try:
                    xmltree = self._getXML(requesturl, Request, postdata)
                except APIError:
                    return None
                else:
                    result = xmltree.find("result/rowset/row").attrib
                    return {
                        "name" : result["name"],
                        "ID" : int(result["characterID"])
                    }
        elif Request.lower() == "getid":
            requesturl = os.path.join(self.API_URL, "eve/CharacterID.xml.aspx")
            if nameName:
                postdata = {
                    "names" : nameName
                }
                try:
                    xmltree = self._getXML(requesturl, Request, postdata)
                except APIError:
                    return None
                else:
                    result = xmltree.find("result/rowset/row").attrib
                    return result
                    return {
                        "name" : result["name"],
                        "ID" : int(result["characterID"])
                    }
                    
        elif Request.lower() == "characterinfo":
            requesturl = os.path.join(self.API_URL, "eve/CharacterInfo.xml.aspx")
            
            if characterID and str(characterID) == str(self.CHAR_ID):
                postdata = {
                    "characterID" : characterID,
                    "keyID" : self.KEY_ID,
                    "vCode" : self.V_CODE,
                }
            elif characterID and str(characterID) != str(self.CHAR_ID):
                postdata = {
                    "characterID" : characterID
                }
            else:
                return None
            try:
                xmltree = self._getXML(requesturl, Request, postdata)
            except APIError:
                return None
            else:
                returnable = {}
                for xmlRow in xmltree.findall("result/"):
                    if xmlRow.tag != "rowset":
                        returnable[xmlRow.tag] = xmlRow.text
                returnable["corporationHistory"] = [
                   x.attrib for x in xmltree.findall("result/rowset/row")
                ]
                return returnable
                    
        elif Request.lower() == "reftypes":
            requesturl = os.path.join(self.API_URL, "eve/RefTypes.xml.aspx")
            #cache foreve
            xmltree = self._getXML(requesturl, Request, {}, permanent=True)
            refTypes = {}
            for x in xmltree.findall("result/rowset/row"):
                refTypes[int(x.attrib["refTypeID"])] = x.attrib["refTypeName"]
            return refTypes
        
        elif Request.lower() == "skilltree":
            requesturl = os.path.join(self.API_URL, "eve/SkillTree.xml.aspx")
            xmltree = self._getXML(requesturl, Request)
            skillTree = {}
            for skillGroup in xmltree.findall("result/rowset/row"):
                groupName = skillGroup.attrib["groupName"]
                groupID = int(skillGroup.attrib["groupID"])
                for skill in skillGroup.findall("rowset/row"):
                    skillName = skill.attrib["typeName"]
                    groupID = int(skill.attrib["groupID"])
                    skillTypeID = int(skill.attrib["typeID"])
                    published = bool(skill.attrib["published"])
                    skillDescription = skill.find("description").text
                    primaryAttribute_element = skill.find("requiredAttributes/primaryAttribute")
                    if primaryAttribute_element is not None:
                        primaryAttribute = primaryAttribute_element.text
                    else:
                        primaryAttribute = None
                    secondaryAttribute_element = skill.find("reqiredAttributes/secondaryAttribute")
                    if secondaryAttribute_element is not None:
                        secondaryAttribute = secondaryAttribute_element.text
                    else:
                        secondaryAttribute = None
                    requiredAttributes = []
                    skillBonusCollection = []
                    for subtype in skill.findall("rowset/row"):
                        if subtype.attrib.has_key("typeID"):
                            requiredAttributes += [subtype.attrib]
                        elif subtype.attrib.has_key("bonusType"):
                            skillBonusCollection += [subtype.attrib]
                    skillTree[skillTypeID] = {
                        "typeID" : skillTypeID,
                        "groupID" : groupID,
                        "groupName" : groupName,
                        "published" : published,
                        "description" : skillDescription,
                        "primaryAttribute" : primaryAttribute,
                        "secondaryAttribute" : secondaryAttribute,
                        "requiredAttributes" : requiredAttributes,
                        "skillBonusCollection" : skillBonusCollection
                    }
            return skillTree            
                    
    def Corporation(self, Request, corporationID=None):
        """
            Methods for retrieving corporation-related data
            
            Keyword arguments:
            ----------------------------------------------------------------------------------------
            * Request        -- the particular request (see below)
              corporationID  -- the ID of the corporation of interest
            ----------------------------------------------------------------------------------------
            * = required
            
            Request:
            +--------------------------------------------------------------------------------------+
            | (N) publicsheet                                                                      |
            | description : returns various corporation info, currently limited to only the name of|
            |               a corporation                                                          |
            | inputs      : corporationID*                                                         |
            | returns     : dict                                                                   |
            +--------------------------------------------------------------------------------------+
            (N) = No API key required
             *  = required input
        """
        if Request.lower() == "publicsheet":
            if corporationID:
                requesturl = os.path.join(self.API_URL, "corp/CorporationSheet.xml.aspx")
                postdata = {
                    "corporationID" : corporationID
                }
                try:
                    xmltree = self._getXML(requesturl, Request, postdata)
                except APIError:
                    return None
                infodict = {}
                for tag in xmltree.findall("result/*"):
                    if tag.tag in ["corporationID", "ceoID", "stationID", "allianceID", "taxRate",
                               "memberCount", "shares"]:
                        infodict[tag.tag] = int(tag.text)
                    elif tag.tag == "logo":
                        infodict["logo"] = dict([(x.tag, x.text) for x in tag.findall("*")])
                    elif tag.tag == "ticker":
                        infodict["corporationTicker"] = tag.text
                    else:
                        infodict[tag.tag] = tag.text
                return infodict

    def Char(self, Request, mailID=None, refID=None, listID=None): #needs updating
        """ Methods for character-related data
        
            (NOTE: all times and dates are returned as floats representing the time since the start
                   of the unix epoch)
            
            Keyword arguments:
            ----------------------------------------------------------------------------------------
            * Request -- the particular request (see below)
              mailID  -- the ID of a mail (see mail request)
              refID   -- the ID of a wallet journal entry (currently not used)
            ----------------------------------------------------------------------------------------
            * = required
            
            Request:
            +--------------------------------------------------------------------------------------+
            | (F) balance                                                                          |
            | description : returns the account balance                                            |
            | inputs      : none                                                                   |
            | returns     : dict with keys accountID, accountKey and accountBalance                |
            +--------------------------------------------------------------------------------------+ 
            | (F) assets                                                                           |
            | description : returns all assets                                                     |
            | inputs      : none                                                                   | 
            | returns     : dict with key itemID (int)                                             |   
            |               each itemID has keys itemID, locationID, typeID, quantity, flag,       |
            |               singleton, __child__ and __contents__                                  |
            |               if __child__ is True, the itemID is a child of another itemID          |
            |               (i.e. contained within it)                                             |
            |               if __contents__ is not None, then this will contain a dict with the    |
            |               same keys as a normal itemID                                           |
            +--------------------------------------------------------------------------------------+               
            | (L) charsheet                                                                        |
            | description : returns various (non-exhaustive) information about the instanced       |
            |               character                                                              |
            | inputs      : none                                                                   |
            | returns     : dict with keys:                                                        | 
            |                 characterID, name, DoB, race, bloodLine, ancestry, gender,           |
            |                 corporationName, corporationID, allianceName, allianceID, cloneName, |
            |                 cloneSkillPoints, balance, attributes, skills, certificates          |
            |               key "attributes" contains a dict with keys:                            |
            |                 intelligence, memory, charisma, perception, willpower                |  
            |                 (the values include any effects from implants)                       |
            |               key "skills" contains a dict with key typeID (int) and value a dict    |
            |               with keys:                                                             |
            |                 typeID, typeName, skillpoints, level                                 |  
            |               key "certificates" contains a dict with key typeID (int) and value a   |
            |               dict with keys:                                                        | 
            |                 certificateID                                                        |
            +--------------------------------------------------------------------------------------+                 
            | (F) industry                                                                         |
            | description : returns industry jobs for the instanced character                      |
            | inputs      : none                                                                   | 
            | returns     : dict with key jobID (int) and value a dict with keys:                  | 
            |                 jobID, assemblyLineID, containerID, installedItemID,                 |
            |                 installedItemLocationID, installedItemQuantity,                      |  
            |                 installedItemProductivityLevel, installedItemMaterialLevel,          |
            |                 installedItemLicensedProductionRunsRemaining, outputLocationID,      |
            |                 installerID, runs, licensedProductionRuns, installedInSolarSystemID, |
            |                 containerLocationID, materialMultiplier, charMaterialMultipler,      | 
            |                 timeMultiplier, charTimeMultipler, installedItemTypeID, outputTypeID,| 
            |                 containerTypeID, installedItemCopy, completed, completedSuccessfully,|
            |                 installedItemFlag, outputFlag, activityID, completedStatus,          |
            |                 installTime, beginProductionTime, endProductionTime,                 | 
            |                 pauseProductionTime                                                  |
            | (NOTE: industry value data types are not correct, they are currently all strings)    |
            +--------------------------------------------------------------------------------------+
            | (F) kills                                                                            |
            | description : returns the latest kills for the instanced character                   |
            | inputs      : none                                                                   |
            | returns     : dict with key killID (int) and value a dict with keys:                 |
            |                 solarSystemName, shipTypeName, killID, killTime, shipTypeID,         |
            |                 solarSystemID, attackers, dropped                                    |
            |               key "attackers" has value of a list containing dicts with keys:        |
            |                 weaponTypeName, corporationID, damageDone, weaponTypeID,             |
            |                 characterName, shipTypeName, allianceName, finalBlow, allianceID,    |
            |                 shipTypeID, corporationName, characterID                             |
            |               key "dropped" has value of a list containing dicts with keys:          |
            |                 typeID, flag, typeName, qtyDropped, qtyDestroyed                     |
            +--------------------------------------------------------------------------------------+
            | (F) mail                                                                             |
            | description : gets mail for the instanced character                                  |
            | inputs      : mailID                                                                 |
            | returns     : if mailID not specified                                                |
            |                 dict with keys mailID (int) with value a dict with keys:             |
            |                   allianceID, title, corpID, allianceTicker, senderID, allianceName, |
            |                   toCharacters, sentDate, corpName, senderName                       |
            |               if mailID specified                                                    |
            |                 string containing parsed out message body                            |
            +--------------------------------------------------------------------------------------+
            | (F) market *** BROKEN ***                                                            |
            | description : returns market orders for the instanced character                      |
            | inputs      : none                                                                   |
            | returns     : dict with keys orderID (int) with values a dict with keys:             |
            |                 orderID, charID, stationID, volEntered, volRemaining, minVolume,     |
            |                 orderState, typeID, range, accountKey, duration, escrow, bid, issued |
            +--------------------------------------------------------------------------------------+
            | (F) research *** IN DEVELOPMENT ***                                                  |
            | description : returns research jobs for the instanced character                      |
            | inputs      : none                                                                   |
            | returns     : none                                                                   |
            +--------------------------------------------------------------------------------------+
            | (L) currentskill                                                                     |
            | description : returns the skill that is currently training                           |
            | inputs      : none                                                                   |
            | returns     : dict with keys:                                                        |
            |                 trainingStartSP, trainingTypeID, trainingDestinationSP,              |
            |                 trainingEndTime, skillInTraining, trainingStartTime, trainingToLevel |
            +--------------------------------------------------------------------------------------+
            | (L) skillqueue                                                                       |
            | description : returns the skill queue                                                |
            | inputs      : none                                                                   |
            | returns     : dict with key queueNumber (int) with value a dict with keys:           |
            |                 typeID, level, endSP, typeName, startTime, startSP, endTime          |
            +--------------------------------------------------------------------------------------+
            | (F) wallet                                                                           |
            | description : returns (the first page of) the wallet journal                         |
            | inputs      : none                                                                   |
            | returns     : dict with key refID (int) with value a dict with keys:                 |
            |                 ownerID2, taxAmount, ownerID1, argID1, taxReceiverID, ownerName2,    |
            |                 reason, argName1, ownerName1, amount, _kills_, taxReceiverName,      |
            |                 refTypeName, date, refTypeID, balance, refID                         |
            |               key "_kills_" (if not None) has value a list containing dicts with     |
            |               keys:                                                                  |
            |                 count, shipName, shipID                                              |
            +--------------------------------------------------------------------------------------+
            | (F) transacts *** IN DEVELOPMENT ***                                                 |
            | description : returns wallet transactions for the instanced character                |
            | inputs      : none                                                                   |
            | returns     : none                                                                   |
            +--------------------------------------------------------------------------------------+
            (F) = Full API key required
            (L) = Limited API key required
            (N) = No API key required
             *  = required input
        """

        basepostdata = {
            "keyID" : self.KEY_ID,
            "vCode" : self.V_CODE,
            "characterID" : self.CHAR_ID
        }

        if Request.lower() == "balance":
            requesturl = os.path.join(self.API_URL, "char/AccountBalance.xml.aspx")
            xmltree = self._getXML(requesturl, Request, basepostdata)
            result = xmltree.find("result/rowset/row")
            return {
                "accountID" : int(result.attrib["accountID"]),
                "accountKey" : result.attrib["accountKey"],
                "balance" : float(result.attrib["balance"]),
            }

        elif Request.lower() == "assets":
            requesturl = os.path.join(self.API_URL, "char/AssetList.xml.aspx")
            xml = self._getXML(requesturl, Request, basepostdata, raw=True)
            assetDict = {}
            rows = re.findall("\<row itemID=\"(\d+)\" locationID=\"(\d+)\" typeID=\"(\d+)\" quantity=\"(\d+)\" flag=\"(\d+)\" singleton=\"(\d+)\" \/\>", xml)
            for row in rows:
                if row[5] == "0":
                    singleton = False
                else:
                    singleton = True
                assetDict.update({row[0] : 
                    {
                        "itemID" : row[0],
                        "locationID" : row[1],
                        "typeID" : row[2],
                        "quantity" : row[3],
                        "flag" : row[4],
                        "singleton" : singleton,
                        "_child_" : False,
                        "_contents_" : None
                    }})
            container_rows = re.findall("(\<row itemID=\"(\d+)\" locationID=\"(\d+)\" typeID=\"(\d+)\" quantity=\"(\d+)\" flag=\"(\d+)\" singleton=\"(\d+)\"\>)", xml)
            lines = [x.strip() for x in xml.split("\n")]
            for container_row in container_rows:
                itemID = container_row[1]
                locationID = container_row[2]
                typeID = container_row[3]
                quantity = container_row[4]
                flag = container_row[5]
                singleton = container_row[6]
                if singleton == "0":
                    singleton = False
                else:
                    singleton = True
                index = lines.index(container_row[0]) + 1
                remains = lines[index:]
                children = []
                for line in remains:
                    result = re.findall("\<row itemID=\"(\d+)\" typeID=\"(\d+)\" quantity=\"(\d+)\" flag=\"(\d+)\" singleton=\"(\d+)\" \/\>", line)
                    try:
                        itemID_child = result[0][0]
                        typeID_child = result[0][1]
                        quantity_child = result[0][2]
                        flag_child = result[0][3]
                        singleton_child = result[0][4]
                        if singleton_child == "0":
                            singleton_child = False
                        else:
                            singleton_child = True
                    except IndexError:
                        pass
                    else:
                        children += [itemID_child]
                        assetDict[itemID_child] = {
                            "itemID" : itemID_child,
                            "locationID" : locationID,
                            "typeID" : typeID_child,
                            "quantity" : quantity_child,
                            "flag" : flag_child,
                            "singleton" : singleton_child,
                            "_child_" : True,
                            "_contents_" : None
                        }
                assetDict[itemID] = {
                    "itemID" : itemID,
                    "locationID" : locationID,
                    "typeID" : typeID,
                    "quantity" : quantity,
                    "flag" : flag,
                    "singleton" : singleton,
                    "_child_" : False,
                    "_contents_" : children
                }
            return assetDict
        elif Request.lower() == "charsheet":
            requesturl = os.path.join(self.API_URL, "char/CharacterSheet.xml.aspx")
            xmltree = self._getXML(requesturl, Request, basepostdata)
            
            data = {}
            for elem in xmltree.findall("result/*"):
                if elem.tag in ["characterID", "corporationID", "allianceID", "cloneSkillPoints"]:
                    data[elem.tag] = int(elem.text)
                elif elem.tag == "balance":
                    data[elem.tag] = float(elem.text)
                elif elem.tag == "attributeEnhancers":
                    attributeEnhancers = {}
                    for attributeEnhanced in elem.findall("*"):
                        augmentatorName = attributeEnhanced.find("augmentatorName").text
                        augmentatorValue = int(attributeEnhanced.find("augmentatorValue").text)
                        attributeEnhancers[attributeEnhanced.tag] = {
                            "augmentatorName" : augmentatorName,
                            "augmentatorValue" : augmentatorValue,
                        }
                    data[elem.tag] = attributeEnhancers
                elif elem.tag == "attributes":
                    data[elem.tag] = dict([(x.tag, int(x.text)) for x in elem.findall("*")])
                elif elem.tag == "DoB":
                    data[elem.tag] = elem.text
                    data["DoBTime"] = self._convertEveToUnix(elem.text)
                elif elem.tag == "rowset":
                    elemName = elem.attrib["name"]
                    if elemName == "skills":
                        skills = {}
                        totalsp = 0
                        for row in elem.findall("row"):
                            skills[int(row.attrib["typeID"])] = {
                                "typeID" : int(row.attrib["typeID"]),
                                "skillpoints" : int(row.attrib["skillpoints"]),
                                "level" : int(row.attrib["level"]),
                            }
                            totalsp += int(row.attrib["skillpoints"])
                        data["skills"] = skills
                        data["totalskillpoints"] = totalsp
                    elif elemName == "certificates":
                        data["certificates"] = [int(x.attrib["certificateID"]) for x in elem.findall("row")]
                    elif elemName in ["corporationRoles", "corporationRolesAtHQ",
                                      "corporationRolesAtBase", "corporationRolesAtOther"]:
                        corpRoles = {}
                        for row in elem.findall("row"):
                            corpRoles[int(row.attrib["roleID"])] = {
                                "roleID" : int(row.attrib["roleID"]),
                                "roleName" : row.attrib["roleName"],
                            }
                        
                        data[elemName] = corpRoles
                    elif elemName == "corporationTitles":
                        data["corporationTitles"] = dict([(int(x.attrib["titleID"]), x.attrib["titleName"]) for x in elem.findall("row")])
                else:
                    data[elem.tag] = elem.text
            return data
            
            def getBasicValue(valueName, xml=xml):
                try:
                    value = xml.split("<%s>" % valueName)[1].split("</%s>" % valueName)[0]
                    return value
                except IndexError:
                    return None
            
            #get attributes
            attrib_dict = {}
            attrib_xml = getBasicValue("attributes").strip()
            attrib_dict["intelligence"] = int(getBasicValue("intelligence",attrib_xml))
            attrib_dict["memory"] = int(getBasicValue("memory", attrib_xml))
            attrib_dict["charisma"] = int(getBasicValue("charisma",attrib_xml))
            attrib_dict["perception"] = int(getBasicValue("perception", attrib_xml))
            attrib_dict["willpower"] = int(getBasicValue("willpower", attrib_xml))
            
            #get attributeEnhancers
            xml_aE = getBasicValue("attributeEnhancers")
            if xml_aE:
                xml_aE = xml_aE.strip()
                intelligence_xml = getBasicValue("intelligenceBonus", xml_aE)
                if intelligence_xml:
                    try:
                        intelligence_bonus_name = getBasicValue("augmentatorName", intelligence_xml)
                        intelligence_bonus_value = int(getBasicValue("augmentatorValue", intelligence_xml))
                        attrib_dict["intelligence"] += intelligence_bonus_value
                    except AttributeError:
                        pass
                memory_xml = getBasicValue("memoryBonus", xml_aE)
                if memory_xml:
                    try:
                        attrib_dict["memory"] += int(getBasicValue("augmentatorValue", memory_xml))
                    except AttributeError:
                        pass
                charisma_xml = getBasicValue("charismaBonus", xml_aE)
                if charisma_xml:
                    try:
                        attrib_dict["charisma"] += int(getBasicValue("augmentatorValue", memory_xml))
                    except AttributeError:
                        pass
                perception_xml = getBasicValue("perceptionBonus", xml_aE)
                if perception_xml:
                    try:
                        attrib_dict["perception"] += int(getBasicValue("augmentatorValue", memory_xml))
                    except AttributeError:
                        pass
                willpower_xml = getBasicValue("willpowerBonus", xml_aE)
                if willpower_xml:
                    try:
                        attrib_dict["willpower"] += int(getBasicValue("augmentatorValue", memory_xml))
                    except AttributeError:
                        pass
                    
            #get skills
            xml_skills = xml.split("<rowset name=\"skills\"")[1].split(">", 1)[1].split("</rowset>")[0]
            rows = re.finditer("\<row typeID=\"(?P<typeID>\d+)\" skillpoints=\"(?P<skillpoints>\d+)\" level=\"(?P<level>\d+)\" \/\>", xml_skills)
            skills_dict = {}
            while True:
                try:
                    row = rows.next().groupdict()
                except StopIteration:
                    break
                else:
                    skills_dict[int(row["typeID"])] = {
                        "typeID" : int(row["typeID"]),
                        "typeName" : self.EVE.getItemNameByID(int(row["typeID"])),
                        "skillpoints" : int(row["skillpoints"]),
                        "level" : int(row["level"])
                    }
                    
            #get certificates
            xml_certs = xml.split("<rowset name=\"certificates\"")[1].split(">", 1)[1].split("</rowset>")[0]
            rows = re.finditer("\<row certificateID=\"(?P<ID>\d+)\" \/\>", xml_certs)
            certificate_dict = {}
            while True:
                try:
                    row = rows.next().groupdict()
                except StopIteration:
                    break
                else:
                    certificate_dict[int(row["ID"])] = {
                        "certificateID" : int(row["ID"]),
                        #"certificateName" : need corresponding method in evedb
                    }
                    
            #ignore corp roles for now
            
            return {
                "characterID" : int(getBasicValue("characterID")),
                "name" : getBasicValue("name"),
                "DoB" : self._convertEveToUnix(getBasicValue("DoB")),
                "race" : getBasicValue("race"),
                "bloodLine" : getBasicValue("bloodLine"),
                "ancestry" : getBasicValue("ancestry"),
                "gender" : getBasicValue("gender"),
                "corporationName" : getBasicValue("corporationName"),
                "corporationID" : int(getBasicValue("corporationID")),
                "allianceName" : getBasicValue("allianceName"),
                "allianceID" : int(getBasicValue("allianceID")),
                "cloneName" : getBasicValue("cloneName"),
                "cloneSkillPoints" : int(getBasicValue("cloneSkillPoints")),
                "balance" : float(getBasicValue("balance")),
                "attributes" : attrib_dict,
                "skills" : skills_dict,
                "certificates" : certificate_dict
            }

        elif Request.lower() == "kills":
            requesturl = os.path.join(self.API_URL, "char/Killlog.xml.aspx")
            xmltree = self._getXML(requesturl, Request, basepostdata)
            killData = {}
            for kill in xmltree.findall("result/rowset/row"):
                v = kill.find("victim").attrib
                victim = {
                    "characterID" : int(v["characterID"]),
                    "characterName" : v["characterName"],
                    "corporationID" : int(v["corporationID"]),
                    "corporationName" : v["corporationName"],
                    "allianceID" : int(v["allianceID"]),
                    "allianceName" : v["allianceName"],
                    "factionID" : int(v["factionID"]),
                    "factionName" : v["factionName"],
                    "damageTaken" : int(v["damageTaken"]),
                    "shipTypeID" : int(v["shipTypeID"]),
                    "shipTypeName" : self.EVE.getItemNameByID(int(v["shipTypeID"])),
                }
                
                for rowset in kill.findall("rowset"):
                    if rowset.attrib["name"] == "attackers":
                        attackers = []
                        attribs = rowset.attrib["columns"].split(",")
                        for attacker in rowset.findall("row"):
                            attackerData = {}
                            for attrib in attribs:
                                if attrib in ["characterID", "corporationID", "allianceID",
                                              "factionID", "damageDone"]:
                                    attackerData[attrib] = int(attacker.attrib[attrib])
                                elif attrib == "securityStatus":
                                    attackerData[attrib] = float(attacker.attrib[attrib])
                                elif attrib in ["weaponTypeID", "shipTypeID"]:
                                    attackerData[attrib] = int(attacker.attrib[attrib])
                                    if attrib == "weaponTypeID":
                                        attackerData["weaponTypeName"] = self.EVE.getItemNameByID(int(attacker.attrib[attrib]))
                                    elif attrib == "shipTypeID":
                                        attackerData["shipTypeName"] = self.EVE.getItemNameByID(int(attacker.attrib[attrib]))
                                else:
                                    attackerData[attrib] = attacker.attrib[attrib]
                            attackers += [attackerData]
                    elif rowset.attrib["name"] == "items":
                        items = []
                        attribs = rowset.attrib["columns"].split(",")
                        for item in rowset.findall("row"):
                            itemData = {}
                            for attrib in attribs:
                                if attrib in ["qtyDropped", "qtyDestroyed"]:
                                    itemData[attrib] = int(item.attrib[attrib])
                                elif attrib == "singleton":
                                    if item.attrib[attrib] == "2":
                                        itemData["blueprintCopy"] = True
                                    else:
                                        itemData["blueprintCopy"] = False
                                elif attrib == "typeID":
                                    itemData["typeID"] = int(item.attrib["typeID"])
                                    itemData["typeName"] = self.EVE.getItemNameByID(int(item.attrib["typeID"]))
                                elif attrib == "flag":
                                    flag = int(item.attrib[attrib])
                                    itemData[attrib] = flag
                                    ### WRITE IN modules.evedb.getFlagNameByID() ###
                                else:
                                    itemData[attrib] = item.attrib[attrib]
                            items += [itemData]
                killData[int(kill.attrib["killID"])] = {
                    "killID" : int(kill.attrib["killID"]),
                    "solarSystemID" : int(kill.attrib["solarSystemID"]),
                    "killTime" : kill.attrib["killTime"],
                    "killTime_" : self._convertEveToUnix(kill.attrib["killTime"]),
                    "victim" : victim,
                    "attackers" : attackers,
                    "items" : items,
                }
                #return {
                #    "killID" : int(kill.attrib["killID"]),
                #    "solarSystemID" : int(kill.attrib["solarSystemID"]),
                #    "killTime" : kill.attrib["killTime"],
                #    "killTime_" : self._convertEveToUnix(killTime),
                #    "victim" : victim
                #}
            
            return killData
        
        elif Request.lower() == "mail":
            if not mailID:
                requesturl = os.path.join(self.API_URL, "char/MailMessages.xml.aspx")
                xmltree = self._getXML(requesturl, Request, basepostdata)
                attribs = xmltree.find("result/rowset").attrib["columns"].split(",")
                mails = {}
                for mailMessage in xmltree.findall("result/rowset/row"):
                    mailData = {}
                    for attrib in attribs:
                        if attrib == "messageID":
                            mailData[attrib] = int(mailMessage.attrib[attrib])
                        elif attrib == "senderID":
                            mailData[attrib] = int(mailMessage.attrib[attrib])
                            mailData["senderName"] = self.Eve("getName", nameID=int(mailMessage.attrib[attrib]))["name"]
                        elif attrib == "toCorpOrAllianceID":
                            ID = int(mailMessage.attrib[attrib])
                            #check if alliance
                            allianceInfo = self.Eve("alliances", allianceID=ID)
                            for to in ["allianceID", "allianceName", "allianceTicker", "corpID", "corpName", "corpTicker"]:
                                mailData[to] = None
                            if allianceInfo:
                                mailData["allianceID"] = ID
                                mailData["allianceName"] = allianceInfo["allianceName"]
                                mailData["allianceTicker"] = allianceInfo["allianceTicker"]
                            else:
                                #check if corp
                                corpInfo = self.Corporation("publicsheet", corporationID=ID)
                                if corpInfo:
                                    mailData["corpID"] = ID
                                    mailData["corpName"] = corpInfo["corporationName"]
                                    mailData["corpTicker"] = corpInfo["corporationTicker"]
                        elif attrib == "toListID":
                            listID = mailMessage.attrib[attrib]
                            if listID:
                                listInfo = self.Char("mailinglists", listID=int(listID))
                                mailData["listID"] = listInfo["listID"]
                                mailData["listName"] = listInfo["displayName"]
                            else:
                                mailData["listID"] = None
                                mailData["listName"] = None
                        elif attrib == "sentDate":
                            mailData[attrib] = mailMessage.attrib[attrib]
                            mailData["sentTime"] = self._convertEveToUnix(mailMessage.attrib[attrib])
                        else:
                            mailData[attrib] = mailMessage.attrib[attrib]
                        #messageID,senderID,sentDate,title,toCorpOrAllianceID,
                        #toCharacterIDs,toListID
                    return mailData
                    mails[int(mailMessage.attrib["messageID"])] = mailData
                return mails
                        
                return xmltree
                                
                        #maildict[int(row["messageID"])] = {
                        #    "senderID" : int(row["senderID"]),
                        #    "senderName" : self.Eve("getName", nameID=int(row["senderID"]))["Name"],
                        #    "sentDate" : calendar.timegm(time.strptime(row["sentDate"], "%Y-%m-%d %H:%M:%S")),
                        #    "title" : row["title"],
                        #    "corpID" : corpID,
                        #    "corpName" : corpName,
                        #    "allianceID" : allianceID,
                        #    "allianceName" : allianceName,
                        #    "allianceTicker" : allianceTicker,
                        #    "toCharacters" : toCharDict
                        #}
                return maildict
            
            else:
                postdata = {
                    "keyID" : self.KEY_ID,
                    "vCode" : self.V_CODE,
                    "characterID" : self.CHAR_ID,
                    "ids" : mailID
                }

                requesturl = os.path.join(self.API_URL, "char/MailBodies.xml.aspx")
                xmltree = self._getXML(requesturl, "mailbodies", postdata)
                message = xmltree.find("result/rowset/row")
                if message is not None:
                    return message.text
        
        elif Request.lower() == "mailinglists":
            requesturl = os.path.join(self.API_URL, "char/mailinglists.xml.aspx")
            xmltree = self._getXML(requesturl, Request, basepostdata)
        
            lists_ = xmltree.findall("result/rowset/row")
            lists = {}
            for list in lists_:
                lists[int(list.attrib["listID"])] = {
                    "listID" : int(list.attrib["listID"]),
                    "displayName" : list.attrib["displayName"]
                }
            if listID:
                if int(listID) not in lists.keys():
                    return None
                else:
                    return lists[listID]
            else:
                return lists
            
            
        elif Request.lower() == "market":
            requesturl = os.path.join(self.API_URL, "char/MarketOrders.xml.aspx")
            xmltree = self._getXML(requesturl, Request, basepostdata)
            attribs = xmltree.find("result/rowset").attrib["columns"].split(",")
            orders = {}
            for order in xmltree.findall("result/rowset/row"):
                orderData = {}
                for attrib in attribs:
                    if attrib in ["escrow", "price"]:
                        orderData[attrib] = float(order.attrib[attrib])
                    elif attrib == "bid":
                        orderData[attrib] = bool(int(order.attrib[attrib]))
                    elif attrib == "orderState":
                        orderData[attrib] = int(order.attrib[attrib])
                        orderLookup = {
                            "0" : "open/active",
                            "1" : "closed",
                            "2" : "expired/fufilled",
                            "3" : "cancelled",
                            "4" : "pending",
                            "5" : "character deleted"
                        }
                        orderData["orderStateName"] = orderLookup[order.attrib[attrib]]
                    elif attrib == "issued":
                        orderData[attrib] = order.attrib[attrib]
                        orderData["issuedTime"] = self._convertEveToUnix(order.attrib[attrib])
                        active_sec = time.time() - orderData["issuedTime"]
                        duration_sec = int(order.attrib["duration"])*24*60*60
                        remaining = duration_sec - active_sec
                        orderData["remainingTime"] = remaining
                        orderData["remaining"] = functions.convert_to_human(remaining)
                    elif attrib == "charID":
                        orderData[attrib] = int(order.attrib[attrib])
                        orderData["charName"] = self.Eve("getName", nameID=orderData[attrib])["name"]
                    elif attrib == "range":
                        orderLookup = {
                            "-1" : "station",
                            "0" : "solar system",
                            "32767" : "region"
                        }
                        range = order.attrib[attrib]
                        orderData[attrib] = int(range)
                        if range in orderLookup.keys():
                            orderData["rangeText"] = orderLookup[range]
                        else:
                            orderData["rangeText"] = "%s jumps" % range
                    elif attrib == "stationID":
                        ID = int(order.attrib[attrib])
                        orderData[attrib] = ID
                        orderData["stationName"] = self.Eve("getName", nameID=ID)["name"]
                    elif attrib == "typeID":
                        ID = int(order.attrib[attrib])
                        orderData[attrib] = ID
                        orderData["typeName"] = self.EVE.getItemNameByID(ID)
                    else:
                        orderData[attrib] = int(order.attrib[attrib])
                orders[int(order.attrib["orderID"])] = orderData
            return orders
            
        elif Request.lower() == "currentskill":
            requesturl = os.path.join(self.API_URL, "char/SkillInTraining.xml.aspx")
            xmltree = self._getXML(requesturl, Request, basepostdata)
            results = {}
            for result in xmltree.findall("result/*"):
                if result.tag == "currentTQTime":
                    pass
                elif "Time" in result.tag:
                    results[result.tag.replace("Time","Date")] = result.text
                    results[result.tag] = self._convertEveToUnix(result.text)
                else:
                    results[result.tag] = int(result.text)
            return results
            
        elif Request.lower() == "skillqueue":
            requesturl = os.path.join(self.API_URL, "char/SkillQueue.xml.aspx")
            xmltree = self._getXML(requesturl, Request, basepostdata)
            returnable = {}
            for queued in xmltree.findall("result/rowset/row"):
                queuePos = int(queued.attrib["queuePosition"])
                returnable[queuePos] = {
                    "queuePosition" : queuePos,
                    "typeID" : int(queued.attrib["typeID"]),
                    "typeName" : self.EVE.getItemNameByID(int(queued.attrib["typeID"])),
                    "level" : int(queued.attrib["level"]),
                    "startSP" : int(queued.attrib["startSP"]),
                    "endSP" : int(queued.attrib["endSP"]),
                    "startTime" : self._convertEveToUnix(queued.attrib["startTime"]),
                    "startDate" : queued.attrib["startTime"],
                    "endTime" : self._convertEveToUnix(queued.attrib["endTime"]),
                    "endDate" : queued.attrib["endTime"]
                }
            return returnable
            
    def Account(self, Request):
        """ Methods for retrieving account-related data
        
            Keyword arguments:
            ----------------------------------------------------------------------------------------
            * Request  -- defines which method will be used
            ----------------------------------------------------------------------------------------
            * = required
            
            Request:
            +--------------------------------------------------------------------------------------+
            | (L) characters                                                                       |
            | description : returns a list of characters                                           |
            | inputs      : none                                                                   |
            | returns     : dict with key characterName (str) with value a dict with keys:         |
            |                 corporationName, corporationID, name, characterID                    |
            +--------------------------------------------------------------------------------------+
            | (F) status                                                                           |
            | description : returns account status                                                 |
            | inputs      : none                                                                   |
            | returns     : dict with keys logonMinutes, createDate, paidUntil, logonCount         |
            +--------------------------------------------------------------------------------------+
            (L) = Limited API key required
            (F) = Full API key required
        """

        if Request.lower() == "characters":
            requesturl = os.path.join(self.API_URL, "account/Characters.xml.aspx")
            postdata = {
                "keyID" : self.KEY_ID,
                "vCode" : self.V_CODE
            }
        
            xmltree = self._getXML(requesturl, Request, postdata)
            returnable = {}
            for x in xmltree.findall("result/rowset/row"):
                returnable[x.attrib["name"]] = {
                    "corporationName" : x.attrib["corporationName"],
                    "corporationID" : int(x.attrib["corporationID"]),
                    "name" : x.attrib["name"],
                    "characterID" : int(x.attrib["characterID"]),
                }
            return returnable

        elif Request.lower() == "status":
            requesturl = os.path.join(self.API_URL, "account/AccountStatus.xml.aspx")
            postdata = {
                "keyID" : self.KEY_ID,
                "vCode" : self.V_CODE,
            }
            
            xmltree = self._getXML(requesturl, Request, postdata)
            
            return {
                "paidUntil" : xmltree.find("result/paidUntil").text,
                "createDate" : xmltree.find("result/createDate").text,
                "logonCount" : int(xmltree.find("result/logonCount").text),
                "logonMinutes" : int(xmltree.find("result/logonMinutes").text),
                "paidUntilTime" : self._convertEveToUnix(xmltree.find("result/paidUntil").text),
                "createTime" : self._convertEveToUnix(xmltree.find("result/createDate").text),
                "logonMinutesHuman" : functions.convert_to_human(int(xmltree.find("result/logonMinutes").text)*60),
            }
            
    def Map(self, Request, systemname):
        """
            Methods for map-related data
            
            Keyword arguments:
            ----------------------------------------------------------------------------------------
            * Request     -- the particular request
            * systemname  -- name of the system of interest
            ----------------------------------------------------------------------------------------
            * = required
            
            Request:
            +--------------------------------------------------------------------------------------+
            | (N) jumps    *** IN DEVELOPMENT ***                                                  |
            | description : returns the number of jumps into the given system                      |
            | inputs      : none                                                                   |
            | returns     : none                                                                   |
            +--------------------------------------------------------------------------------------+
            | (N) kills                                                                            |
            | description : returns the number of (PvP) kills in the given system                  |
            | inputs      : systemname*                                                            |
            | returns     : dict with keys podKills, npcKills, solarSystemID, shipKills,           |
            |               solarSystemName                                                        |
            +--------------------------------------------------------------------------------------+
            | (N) sov                                                                              |
            | description : returns sovreignty information for a given system                      |
            | inputs      : systemname*                                                            |
            | returns     : dict with keys corporationID, allianceID, solarSystemName, factionName,|
            |               allianceTicker, allianceName, factionID, corporationName, solarSystemID|
            +--------------------------------------------------------------------------------------+
            (N) = no API key required
             *  = required input
        """
        solarSystemID_str = self.EVE.getSystemIDByName(systemname)
        if solarSystemID_str:
            solarSystemID = int(solarSystemID_str)
        else:
            return None
        
        if Request.lower() == "jumps":
            requesturl = os.path.join(self.API_URL, "map/Jumps.xml.aspx")
            #solarSystemID_str
            xmltree = self._getXML(requesturl, Request)
            for system in xmltree.findall("result/rowset/row"):
                if int(system.attrib["solarSystemID"]) == solarSystemID:
                    return {
                        "shipJumps" : int(system.attrib["shipJumps"]),
                        "solarSystemID" : int(system.attrib["solarSystemID"]),
                        "solarSystemName" : self.EVE.getSystemNameByID(solarSystemID)
                    }

        if Request.lower() == "kills":
            requesturl = os.path.join(self.API_URL, "map/Kills.xml.aspx")
            xmltree = self._getXML(requesturl, Request)
            for system in xmltree.findall("result/rowset/row"):
                if int(system.attrib["solarSystemID"]) == solarSystemID:
                    return {
                        "solarSystemID" : int(system.attrib["solarSystemID"]),
                        "solarSystemName" : self.EVE.getSystemNameByID(solarSystemID),
                        "shipKills" : int(system.attrib["shipKills"]),
                        "factionKills" : int(system.attrib["factionKills"]),
                        "podKills" : int(system.attrib["podKills"])
                    }
            return {
                "solarSystemID" : solarSystemID,
                "solarSystemName" : self.EVE.getSystemNameByID(solarSystemID),
                "shipKills" : 0,
                "podKills" : 0,
                "npcKills" : 0
            }

        if Request.lower() == "sov":
            requesturl = os.path.join(self.API_URL, "map/Sovereignty.xml.aspx")
            xmltree = self._getXML(requesturl, Request)
            for system in xmltree.findall("result/rowset/row"):
                if int(system.attrib["solarSystemID"]) == solarSystemID:
                    if system.attrib["allianceID"] != "0":
                        allianceInfo = self.Eve("alliances", allianceID=int(system.attrib["allianceID"]))
                        corporationInfo = self.Corporation("publicsheet", int(system.attrib["corporationID"]))
                        return {
                            "allianceName" : allianceInfo["allianceName"],
                            "allianceID" : int(system.attrib["allianceID"]),
                            "allianceTicker" : allianceInfo["allianceTicker"],
                            "solarSystemID" : solarSystemID,
                            "solarSystemName" : self.EVE.getSystemNameByID(solarSystemID),
                            "factionID" : None,
                            "factionName" : None,
                            "corporationID" : int(system.attrib["corporationID"]),
                            "corporationName" : corporationInfo["corporationName"],
                            "corporationTicker" : corporationInfo["corporationTicker"],
                        }
                    elif system.attrib["factionID"] != "0":
                        return {
                            "allianceName" : None,
                            "allianceID" : None,
                            "allianceTicker" : None,
                            "solarSystemID" : solarSystemID,
                            "solarSystemName" : self.EVE.getSystemNameByID(solarSystemID),
                            "factionID" : int(system.attrib["factionID"]),
                            "factionName" : self.EVE.getFactionNameByID(system.attrib["factionID"]),
                            "corporationID" : None,
                            "corporationName" : None,
                            "corporationTicker" : None,
                        }
                    else:
                        return {
                            "allianceName" : None,
                            "allianceID" : None,
                            "allianceTicker" : None,
                            "solarSystemID" : solarSystemID,
                            "solarSystemName" : self.EVE.getSystemNameByID(solarSystemID),
                            "factionID" : None,
                            "factionName" : None,
                            "corporationID" : None,
                            "corporationName" : None,
                            "corporationTicker" : None,
                        }

    def EveCentral(self, Request, itemID, regionID=None):

        if Request.lower() == "marketstat":
            ecURL = "http://api.eve-central.com/api/"
            if regionID:
                requesturl = ecURL + "marketstat?typeid=" + itemID + "&regionlimit=" + regionID
            else:
                requesturl = ecURL + "marketstat?typeid=" + itemID
            xml = urllib2.urlopen(requesturl).read()
            try:
                buyVolume, buyAvg, buyMax, buyMin, buyMedian, sellVolume, sellAvg, sellMax, sellMin, sellMedian = re.findall("(?s)\<buy\>.*\<volume\>(\d+).*\<avg\>(\d+).*\<max\>(\d+).*\<min\>(\d+).*\<median\>(\d+).[0-9]{0,2}\</median\>.*\<sell\>.*\<volume\>(\d+).*\<avg\>(\d+).*\<max\>(\d+).*\<min\>(\d+).*\<median\>(\d+)", xml)[0]
            except IndexError:
                return None
            else:
                return {
                    "buyVolume" : int(buyVolume),
                    "buyAvg" : int(buyAvg),
                    "buyMax" : int(buyMax),
                    "buyMin" : int(buyMin),
                    "buyMedian" : int(buyMedian),
                    "sellVolume" : int(sellVolume),
                    "sellAvg" : int(sellAvg),
                    "sellMax" : int(sellMax),
                    "sellMin" : int(sellMin),
                    "sellMedian" : int(sellMedian)
                }




    def Server(self, Request):
        """
            Methods for server-related data
            
            Keyword Arguments:
            ----------------------------------------------------------------------------------------
            * Request -- defines which method will be used
            ----------------------------------------------------------------------------------------
            * = required
            
            Request:
            +--------------------------------------------------------------------------------------+
            | (N) status                                                                           |
            | description : returns the current server status                                      |
            | inputs      : none                                                                   |
            | returns     : dict with keys status, online, time                                    |
            +--------------------------------------------------------------------------------------+
            (N) = No API key required
        """

        if Request.lower() == "status":
            requesturl = os.path.join(self.API_URL, "server/ServerStatus.xml.aspx")
            xmltree = etree.parse(StringIO.StringIO(urllib2.urlopen(requesturl).read()))
            serverOpen = xmltree.find("result/serverOpen").text
            if serverOpen == "True":
                status = "Online"
            else:
                status = "Offline"
            return {
                "status" : status,
                "online" : int(xmltree.find("result/onlinePlayers").text),
                "time" : xmltree.find("currentTime").text
            }

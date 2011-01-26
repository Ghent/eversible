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
import evedb
import cache

class APIError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class API:
    def __init__(self, userid=None, apikey=None, charid=None, characterName=None, debug=False):
        self.USER_ID = userid
        self.API_KEY = apikey
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
            self.CHAR_ID = charid
        

    def _getXML(self, requesturl, postdata={}):
        xml = self.CACHE.requestXML(requesturl, postdata)
        if not xml:
            xml = urllib2.urlopen(requesturl, urllib.urlencode(postdata)).read()
            self.CACHE.insertXML(requesturl, xml, self._getCachedUntil(xml), postdata)
        self._errorCheck(xml)
        return xml
        
    def _errorCheck(self, xml):
        try:
            error = re.findall("\<error code=\"(\d+)\"\>(.*?)\<\/error\>",xml)[0]
        except IndexError:
            return None
        else:
            raise APIError("%s : %s" % (error[0], error[1]))
        
    def _getCachedUntil(self, xml):
        cachedUntil = time.mktime(time.strptime(re.findall("\<cachedUntil\>(.*?)\<\/cachedUntil\>", xml)[0], "%Y-%m-%d %H:%M:%S"))
        return cachedUntil
    
    def Eve(self,Request, allianceID=None, nameID=None, nameName=None, allianceName=None, allianceTicker=None, characterID=None):
        """
            Methods related to EVE in general:
            *********************************************
            alliances : returns alliance info for a given
                        allianceID, allianceName or allianceID(N)
                        # currently outputs only allianceID, 
                        # allianceName and allianceTicker
            getName   : returns the Name for a given ID
                        # includes chars, corps and alliances
            getID     : returns the ID for a given Name
                        # includes chars, corps and alliances
            characterinfo : returns (public) info for a character
            refTypes : returns list of wallet journal ref types
            *********************************************
            (N) = No API key required
        """
        if Request.lower() == "alliances":
            requesturl = os.path.join(self.API_URL, "eve/AllianceList.xml.aspx")
            xml = self._getXML(requesturl)
            if allianceID:
                try:
                    allianceName, allianceTicker = re.findall("\<row name=\"(.*?)\" shortName=\"(.*?)\" allianceID=\"%s\"" % (allianceID), xml)[0]
                except IndexError:
                    return None
                else:
                    return {
                        "allianceID" : int(allianceID),
                        "allianceName" : allianceName,
                        "allianceTicker" : allianceTicker
                    }
            elif allianceName:
                try:
                    allName, allianceTicker, allianceID = re.findall("\<row name=\"(%s)\" shortName=\"(.*?)\" allianceID=\"(\d+)\"" % (allianceName), xml, re.I)[0]
                except IndexError:
                    return None
                else:
                    return {
                        "allianceID" : int(allianceID),
                        "allianceName" : allName,
                        "allianceTicker" : allianceTicker
                    }
            elif allianceTicker:
                try:
                    allianceName, Ticker, allianceID = re.findall("\<row name=\"(.*?)\" shortName=\"(%s)\" allianceID=\"(\d+)\"" % (allianceTicker), xml, re.I)[0]
                except IndexError:
                    return None
                else:
                    return {
                        "allianceID" : int(allianceID),
                        "allianceName" : allianceName,
                        "allianceTicker" : Ticker
                    }
            else:
                return None
        elif Request.lower() == "getname":
            requesturl = os.path.join(self.API_URL, "eve/CharacterName.xml.aspx")
            if nameID:
                postdata = {
                    "ids" : nameID
                }
                xml = self._getXML(requesturl, postdata)
                try:
                    charName, charID = re.findall("\<row name=\"(.*?)\" characterID=\"(\d+)\" \/\>", xml)[0]
                except IndexError:
                    return None
                else:
                    return {
                        "Name" : charName,
                        "ID" : int(charID)
                    }
        elif Request.lower() == "getid":
            requesturl = os.path.join(self.API_URL, "eve/CharacterID.xml.aspx")
            if nameName:
                postdata = {
                    "names" : nameName
                }
                xml = self._getXML(requesturl, postdata)
                try:
                    charName, charID = re.findall("\<row name=\"(.*?)\" characterID=\"(\d+)\" \/\>", xml)[0]
                except IndexError:
                    return None
                else:
                    return {
                        "Name" : charName,
                        "ID" : int(charID)
                    }
        elif Request.lower() == "characterinfo":
            requesturl = os.path.join(self.API_URL, "eve/CharacterInfo.xml.aspx")
            def getValue(name):
                try:
                    value = xml.split("<%s>" % name)[1].split("</%s>" % name)[0]
                except IndexError:
                    return None
                else:
                    return value
                
            if characterID:
                postdata = {
                    "characterID" : characterID
                }
                try:
                    xml = self._getXML(requesturl, postdata)
                except APIError:
                    return None
                else:
                    return {
                        "characterID" : int(getValue("characterID")),
                        "characterName" : getValue("characterName"),
                        "race" : getValue("race"),
                        "bloodline" : getValue("bloodline"),
                        "corporationID" : int(getValue("corporationID")),
                        "corporationName" : getValue("corporation"),
                        "corporationDate" : time.mktime(time.strptime(getValue("corporationDate"), "%Y-%m-%d %H:%M:%S")),
                        "allianceID" : int(getValue("allianceID")),
                        "allianceName" : getValue("alliance"),
                        "allianceDate" : time.mktime(time.strptime(getValue("allianceDate"), "%Y-%m-%d %H:%M:%S")),
                        "securityStatus" : float(getValue("securityStatus"))
                    }
        elif Request.lower() == "reftypes":
            requesturl = os.path.join(self.API_URL, "eve/RefTypes.xml.aspx")
            #cache forever
            xml = self.CACHE.requestXML(requesturl, {})
            if not xml:
                xml = urllib2.urlopen(requesturl).read()
                self._errorCheck(xml)
                self.CACHE.insertXML(requesturl, xml, 2147483647.0, {})
            
            rows = re.finditer("\<row refTypeID=\"(?P<refTypeID>\d+)\" refTypeName=\"(?P<refTypeName>.*?)\" \/\>", xml)
            refTypes = {}
            while True:
                try:
                    row = rows.next().groupdict()
                except StopIteration:
                    break
                else:
                    refTypes[int(row["refTypeID"])] = row["refTypeName"]
            return refTypes

                
                    
    def Corporation(self, Request, corporationID=None):
        """
            Methods related to corporations:
            **********************************************
            publicsheet : returns various corporation info
                          for a given corporationID (N)
                          # currently outputs only corporationName
            **********************************************
            (N) = No API key required
        """
        if Request.lower() == "publicsheet":
            if corporationID != "0":
                requesturl = os.path.join(self.API_URL, "corp/CorporationSheet.xml.aspx")
                if corporationID:
                    postdata = {
                        "corporationID" : corporationID
                    }
                else:
                    return None
                try:
                    xml = self._getXML(requesturl, postdata)
                except APIError:
                    return None
                
                corporationName = xml.split("<corporationName>")[1].split("</corporationName>")[0]
                
                return {
                    "corporationID" : corporationID,
                    "corporationName" : corporationName
                }
            else:
                return None
                        
    def Char(self, Request, mailID=None, refID=None):
        """ Methods related to a character:
            **********************************************
            balance : returns the account balance (F)
            assets : returns assets (F)
            charsheet : returns character sheet (L)
            industry : returns industry jobs (F)
            kills : returns kill log (F)
            mail : returns eve mails (F)
            market : returns market orders (F)
            research : returns research jobs (F)
            currentskill : returns the current skill in training (L)
            skillqueue : returns the skill queue (L)
            wallet : returns the wallet journal (F)
            transacts : returns wallet transactions (F)
            **********************************************
            (L) = limited API key required
        """

        basepostdata = {
            "apiKey" : self.API_KEY,
            "userID" : self.USER_ID,
            "characterID" : self.CHAR_ID
        }

        if Request.lower() == "balance":
            requesturl = os.path.join(self.API_URL, "char/AccountBalance.xml.aspx")
            xml = self._getXML(requesurl, basepostdata)
            row = re.search("\<row accountID=\"(?P<accountID>\d+)\" accountKey=\"(?P<accountKey>\d+)\" balance=\"(?P<balance>\d+\.\d+)\" \/\>", xml)
            return {
                "accountID" : row.group("accountID"),
                "accountKey" : row.group("accountKey"),
                "balance" : row.group("balance")
            }

        elif Request.lower() == "assets":
            requesturl = os.path.join(self.API_URL, "char/AssetList.xml.aspx")
            xml = self._getXML(requesturl, basepostdata)
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
            xml = self._getXML(requesturl, basepostdata)
            print xml

        elif Request.lower() == "industry":
            requesturl = os.path.join(self.API_URL, "char/IndustryJobs.xml.aspx")
            xml = self._getXML(requesturl, basepostdata)
            
            regex = re.compile(r"""
                              \<row\ jobID="(?P<jobID>\d+)"\ #unique ID
                              assemblyLineID="(?P<assemblyLineID>\d+)"\ #static if station assembly line
                              containerID="(?P<containerID>\d+)"\ #stationID if in station, itemID of POS module if not (see corporation asset list)
                              installedItemID="(?P<installedItemID>\d+)"\ #bp itemID (see asset list)
                              installedItemLocationID="(?P<installedItemLocationID>\d+)"\ 
                              installedItemQuantity="(?P<installedItemQuantity>\d+)"\ 
                              installedItemProductivityLevel="(?P<installedItemProductivityLevel>\d+)"\ 
                              installedItemMaterialLevel="(?P<installedItemMaterialLevel>\d+)"\ 
                              installedItemLicensedProductionRunsRemaining="(?P<installedItemLicensedProductionRunsRemaining>.*?)"\ 
                              outputLocationID="(?P<outputLocationID>\d+)"\ 
                              installerID="(?P<installerID>\d+)"\ 
                              runs="(?P<runs>\d+)"\ 
                              licensedProductionRuns="(?P<licensedProductionRuns>\d+)"\ 
                              installedInSolarSystemID="(?P<installedInSolarSystemID>\d+)"\ 
                              containerLocationID="(?P<containerLocationID>\d+)"\ 
                              materialMultiplier="(?P<materialMultiplier>\d+)"\ 
                              charMaterialMultiplier="(?P<charMaterialMultiplier>\d+\.\d+)"\ 
                              timeMultiplier="(?P<timeMultiplier>\d+)"\ 
                              charTimeMultiplier="(?P<charTimeMultiplier>\d+\.\d+)"\ 
                              installedItemTypeID="(?P<installedItemTypeID>\d+)"\ 
                              outputTypeID="(?P<outputTypeID>\d+)"\ 
                              containerTypeID="(?P<containerTypeID>\d+)"\ 
                              installedItemCopy="(?P<installedItemCopy>\d+)"\ 
                              completed="(?P<completed>\d+)"\ 
                              completedSuccessfully="(?P<completedSuccessfully>\d+)"\ 
                              installedItemFlag="(?P<installedItemFlag>\d+)"\ 
                              outputFlag="(?P<outputFlag>\d+)"\ 
                              activityID="(?P<activityID>\d+)"\ 
                              completedStatus="(?P<completedStatus>\d+)"\ 
                              installTime="(?P<installTime>\d+-\d+-\d+\ \d+:\d+:\d+)"\ 
                              beginProductionTime="(?P<beginProductionTime>\d+-\d+-\d+\ \d+:\d+:\d+)"\ 
                              endProductionTime="(?P<endProductionTime>\d+-\d+-\d+\ \d+:\d+:\d+)"\ 
                              pauseProductionTime="(?P<pauseProductionTime>\d+-\d+-\d+\ \d+:\d+:\d+)"\ \/\>
                              """, re.VERBOSE)
            rows = regex.finditer(xml)
            return xml, rows, regex
            industrydict = {}
            while True:
                try:
                    row = rows.next()
                    row = row.groupdict()
                except StopIteration:
                    break
                else:
                    industrydict[row["jobID"]] = row
            return industrydict

        elif Request.lower() == "kills":
            requesturl = os.path.join(self.API_URL, "char/Killlog.xml.aspx")
            xml = self._getXML(requesturl, basepostdata)
            if "Kills exhausted" in xml:
                return None
            #open("output.xml","w").write(xml)
            #xml = open("output.xml").read()
            kills = ["<row killID=\"" + x for x in xml.split("<row killID=\"")]
            generalRE = re.compile("\<row killID=\"(?P<killID>\d+)\" solarSystemID=\"(?P<solarSystemID>\d+)\" killTime=\"(?P<killTime>\d+-\d+-\d+ \d+:\d+:\d+)\" moonID=\"(?P<moonID>\d+)\"\>")
            victimRE = re.compile("\<victim characterID=\"(?P<characterID>\d+)\" characterName=\"(?P<characterName>.*?)\" corporationID=\"(?P<corporationID>\d+)\" corporationName=\"(?P<corporationName>.*?)\" allianceID=\"(?P<allianceID>\d+)\" allianceName=\"(?P<allianceName>.*?)\" .*?damageTaken=\"(?P<damageTaken>\d+)\" shipTypeID=\"(?P<shipTypeID>\d+)\" \/\>")
            attackRE = re.compile("\<row characterID=\"(?P<characterID>\d+)\" characterName=\"(?P<characterName>.*?)\" corporationID=\"(?P<corporationID>\d+)\" corporationName=\"(?P<corporationName>.*?)\" allianceID=\"(?P<allianceID>\d+)\" allianceName=\"(?P<allianceName>.*?)\" .*?damageDone=\"(?P<damageDone>\d+)\" finalBlow=\"(?P<finalBlow>\d+)\" weaponTypeID=\"(?P<weaponTypeID>\d+)\" shipTypeID=\"(?P<shipTypeID>\d+)\" \/\>")
            dropRE = re.compile("\<row typeID=\"(?P<typeID>\d+)\" flag=\"(?P<flag>\d+)\" qtyDropped=\"(?P<qtyDropped>\d+)\" qtyDestroyed=\"(?P<qtyDestroyed>\d+)\"")
            killDict = {}
            for kill in kills:
                try:
                    generalData = generalRE.search(kill).groupdict()
                    #{'killID': '14868783', 'solarSystemID': '30002723', 'killTime': '2010-09-29 12:49:00', 'moonID': '0'}
                except:
                    pass
                else:
                    killID = int(generalData["killID"])
                    ATTACKERS = []
                    ATTACK = False
                    DROPS = {}
                    DROP = False
                    CARGO = False
                    dropno = 0
                    for line in kill.split("\n"):
                        if "victim" in line:
                            try:
                                victimData = victimRE.search(line).groupdict()
                            except:
                                pass
                        elif "rowset name=\"attackers\"" in line:
                            ATTACK = True
                        elif "row characterID" in line and ATTACK:
                            try:
                                attackerData = attackRE.search(line).groupdict()
                            except:
                                pass
                            else:
                                ATTACKERS += [attackerData]
                        elif "</rowset>" in line and ATTACK:
                            ATTACK = False
                        elif "rowset name=\"items\"" in line and not DROP and not CARGO:
                            DROP = True
                        elif "</rowset>" in line and DROP and not CARGO:
                            DROP = False
                        elif DROP and not CARGO:
                            if "<rowset name=\"items\"" in line:
                                CARGO = True
                            else:
                                dropno += 1
                                try:
                                    dropData = dropRE.search(line).groupdict()
                                except:
                                    pass
                                else:
                                    DROPS[dropno] = dropData
                        elif CARGO:
                            if "<row typeID" in line:
                                try:
                                    dropData = dropRE.search(line).groupdict()
                                except:
                                    pass
                                else:
                                    if type(CARGO) != list:
                                        CARGO = [dropData]
                                    else:
                                        CARGO += [dropData]
                            elif "</rowset>" in line:
                                DROPS[dropno]["children"] = CARGO
                                CARGO = False
                    #victim data
                    #{'corporationID': '1102238026', 'damageTaken': '286', 'characterName': 'mountainpenguin', 'allianceName': 'Intergalactic Exports Group', 'allianceID': '1076729448', 'shipTypeID': '670', 'corporationName': 'LazyBoyz Band of Recreational Flyers', 'characterID': '1364641301'}
                    victim_shipTypeName = self.EVE.getItemNameByID(int(victimData["shipTypeID"]))
                    namedAttackers = []
                    for attacker in ATTACKERS:
                        weaponTypeName = self.EVE.getItemNameByID(int(attacker["weaponTypeID"]))
                        if weaponTypeName == "#system":
                            weaponTypeName = "Unknown"
                        shipTypeName = self.EVE.getItemNameByID(int(attacker["shipTypeID"]))
                        namedAttackers += [{
                            "corporationID" : int(attacker["corporationID"]),
                            "damageDone" : int(attacker["damageDone"]),
                            "weaponTypeID" : int(attacker["weaponTypeID"]),
                            "weaponTypeName" : self.EVE.getItemNameByID(int(attacker["weaponTypeID"])),
                            "characterName" : attacker["characterName"],
                            "allianceName" : attacker["allianceName"],
                            "finalBlow" : int(attacker["finalBlow"]),
                            "allianceID" : int(attacker["allianceID"]),
                            "shipTypeID" : int(attacker["shipTypeID"]),
                            "shipTypeName" : shipTypeName,
                            "corporationName" : attacker["corporationName"],
                            "characterID" : int(attacker["characterID"])
                        }]
                    namedDrops = []
                    for i,v in DROPS.iteritems():
                        #6 : {'typeID': '3467', 'flag': '5', 'qtyDropped': '0', 'children': [{'typeID': '23594', 'flag': '0', 'qtyDropped': '0', 'qtyDestroyed': '1'}, {'typeID': '2444', 'flag': '0', 'qtyDropped': '0', 'qtyDestroyed': '4'}, {'typeID': '23606', 'flag': '0', 'qtyDropped': '0', 'qtyDestroyed': '1'}, {'typeID': '12093', 'flag': '0', 'qtyDropped': '0', 'qtyDestroyed': '1'}, {'typeID': '12386', 'flag': '0', 'qtyDropped': '0', 'qtyDestroyed': '1'}], 'qtyDestroyed': '1'
                        typeName = self.EVE.getItemNameByID(int(v["typeID"]))
                        namedChilds = []
                        if v.has_key("children"):
                            children = v["children"]
                            for child in children:
                                child_typeName = self.EVE.getItemNameByID(int(child["typeID"]))
                                namedChilds += [{
                                    "typeID" : int(child["typeID"]),
                                    "flag" : int(child["flag"]),
                                    "qtyDropped" : int(child["qtyDropped"]),
                                    "qtyDestroyed" : int(child["qtyDestroyed"]),
                                    "typeName" : child_typeName
                                }]
                        namedDrops += [{
                            "typeID" : int(v["typeID"]),
                            "flag" : int(v["flag"]),
                            "qtyDropped" : int(v["qtyDropped"]),
                            "qtyDestroyed" : int(v["qtyDestroyed"]),
                            "typeName" : typeName
                        }]
                    killDict[int(killID)] = {
                        #generalData {'killID': '14868783', 'solarSystemID': '30002723', 'killTime': '2010-09-29 12:49:00', 'moonID': '0'}
                        "killID" : int(killID),
                        "solarSystemID" : int(generalData["solarSystemID"]),
                        "solarSystemName" : self.EVE.getSystemNameByID(int(generalData["solarSystemID"])),
                        "killTime" : time.mktime(time.strptime(generalData["killTime"], "%Y-%m-%d %H:%M:%S")),
                        "shipTypeID" : int(victimData["shipTypeID"]),
                        "shipTypeName" : victim_shipTypeName,
                        "attackers" : namedAttackers,
                        "dropped" : namedDrops
                    }
            return killDict

        elif Request.lower() == "mail":
            if not mailID:
                requesturl = os.path.join(self.API_URL, "char/MailMessages.xml.aspx")
                xml = self._getXML(requesturl, basepostdata)
                rows = re.finditer("\<row messageID=\"(?P<messageID>\d+)\" senderID=\"(?P<senderID>\d+)\" sentDate=\"(?P<sentDate>\d+-\d+-\d+ \d+:\d+:\d+)\" title=\"(?P<title>.*?)\" toCorpOrAllianceID=\"(?P<toCorpOrAllianceID>\d+)\" toCharacterIDs=\"(?P<toCharacterIDs>.*?)\" toListID=\"(?P<toListID>.*?)\" \/\>", xml)
                maildict = {}
                while True:
                    try:
                        row = rows.next().groupdict()
                    except StopIteration:
                        break
                    else:
                        #resolve corp / alliance recipient
                        tCOAID = int(row["toCorpOrAllianceID"])
                        corpCheck = self.Corporation("publicsheet", tCOAID)
                        if corpCheck:
                            corpID = tCOAID
                            corpName = corpCheck["corporationName"]
                            allianceID = None
                            allianceName = None
                            allianceTicker = None
                        else:
                            allianceCheck = self.Eve("alliances", allianceID=tCOAID)
                            if allianceCheck:
                                corpID = None
                                corpName = None
                                allianceID = tCOAID
                                allianceName = allianceCheck["allianceName"]
                                allianceTicker = allianceCheck["allianceTicker"]
                            else:
                                (corpID, corpName, allianceID, allianceName, allianceTicker) = (None, None, None, None, None)
                                
                        #resolve charIDs
                        toCharIDs = row["toCharacterIDs"]
                        if toCharIDs == "":
                            toCharDict = None
                        else:
                            toCharDict = {}
                            IDs = toCharIDs.split(",")
                            for ID in IDs:
                                charID = int(ID)
                                charCheck = self.Eve("getName", nameID=charID)
                                if charCheck:
                                    charName = charCheck["Name"]
                                    toCharDict[charID] = {"characterName" : charName}
                                
                        maildict[int(row["messageID"])] = {
                            "senderID" : int(row["senderID"]),
                            "senderName" : self.Eve("getName", nameID=int(row["senderID"]))["Name"],
                            "sentDate" : time.mktime(time.strptime(row["sentDate"], "%Y-%m-%d %H:%M:%S")),
                            "title" : row["title"],
                            "corpID" : corpID,
                            "corpName" : corpName,
                            "allianceID" : allianceID,
                            "allianceName" : allianceName,
                            "allianceTicker" : allianceTicker,
                            "toCharacters" : toCharDict
                        }
                return maildict
            
            else:
                postdata = {
                    "apiKey" : self.API_KEY,
                    "userID" : self.USER_ID,
                    "characterID" : self.CHAR_ID,
                    "ids" : mailID
                }

                requesturl = os.path.join(self.API_URL, "char/MailBodies.xml.aspx")
                xml = self._getXML(requesturl, postdata)
                try:
                    message = xml.split("<row messageID=\"%s\"><![CDATA[" % mailID)[1].split("]]></row>")[0]
                except IndexError:
                    return None
                else:
                    return message

        elif Request.lower() == "market":
            requesturl = os.path.join(self.API_URL, "char/MarketOrders.xml.aspx")
            xml = self._getXML(requesturl, basepostdata)
            rows = re.finditer("\<row orderID=\"(?P<orderID>\d+)\" charID=\"(?P<charID>\d+)\" stationID=\"(?P<stationID>\d+)\" volEntered=\"(?P<volEntered>\d+)\" volRemaining=\"(?P<volRemaining>\d+)\" minVolume=\"(?P<minVolume>\d+)\" orderState=\"(?P<orderState>\d+)\" typeID=\"(?P<typeID>\d+)\" range=\"(?P<range>\d+)\" accountKey=\"(?P<accountKey>\d+)\" duration=\"(?P<duration>\d+)\" escrow=\"(?P<escrow>\d+\.\d+)\" bid=\"(?P<bid>\d+)\" issued=\"(?P<issued>\d+-\d+-\d+ \d+:\d+:\d+)\" \/\>", xml)
            returndict = {}
            while True:
                try:
                    row = rows.next().groupdict()
                except StopIteration:
                    break
                else:
                    returndict[row["orderID"]] = row
            return returndict

        elif Request.lower() == "research":
            requesturl = os.path.join(self.API_URL, "char/Research.xml.aspx")
            xml = self._getXML(requesturl, basepostdata)
            print xml
        elif Request.lower() == "currentskill":
            requesturl = os.path.join(self.API_URL, "char/SkillInTraining.xml.aspx")
            xml = self._getXML(requesturl, basepostdata)
            def getValue(id):
                try:
                    value = re.search("\<%s\>(.*?)\<\/%s\>" % (id, id), xml).group(1)
                except:
                    value = None
                return value

            return {
                "trainingEndTime" : getValue("trainingEndTime"),
                "trainingStartTime" : getValue("trainingStartTime"),
                "trainingTypeID" : getValue("trainingTypeID"),
                "trainingStartSP" : getValue("trainingStartSP"),
                "trainingDestinationSP" : getValue("trainingDestinationSP"),
                "trainingToLevel" : getValue("trainingToLevel"),
                "skillInTraining" : getValue("skillInTraining")
            }

        elif Request.lower() == "skillqueue":
            requesturl = os.path.join(self.API_URL, "char/SkillQueue.xml.aspx")
            xml = self._getXML(requesturl, basepostdata)
            
            rows = re.finditer("\<row queuePosition=\"(?P<queuePosition>\d+)\" typeID=\"(?P<typeID>\d+)\" level=\"(?P<level>\d+)\" startSP=\"(?P<startSP>\d+)\" endSP=\"(?P<endSP>\d+)\" startTime=\"(?P<startTime>\d+-\d+-\d+ \d+:\d+:\d+)\" endTime=\"(?P<endTime>\d+-\d+-\d+ \d+:\d+:\d+)\"", xml)
            returndict = {}
            while True:
                try:
                    row = rows.next().groupdict()
                except StopIteration:
                    break
                else:
                    returndict[int(row["queuePosition"])] = {
                        "typeID" : int(row["typeID"]),
                        "typeName" : self.EVE.getItemNameByID(int(row["typeID"])),
                        "level" : int(row["level"]),
                        "startSP" : int(row["startSP"]),
                        "endSP" : int(row["endSP"]),
                        "startTime" : time.mktime(time.strptime(row["startTime"], "%Y-%m-%d %H:%M:%S")),
                        "endTime" : time.mktime(time.strptime(row["endTime"], "%Y-%m-%d %H:%M:%S"))
                    }
            return returndict
        elif Request.lower() == "wallet":
            requesturl = os.path.join(self.API_URL, "char/WalletJournal.xml.aspx")
            xml = self._getXML(requesturl, basepostdata)
            
            walletdict = {}
            rows = re.finditer("\<row date=\"(?P<date>\d+-\d+-\d+ \d+:\d+:\d+)\" refID=\"(?P<refID>\d+)\" refTypeID=\"(?P<refTypeID>\d+)\" ownerName1=\"(?P<ownerName1>.*?)\" ownerID1=\"(?P<ownerID1>\d+)\" ownerName2=\"(?P<ownerName2>.*?)\" ownerID2=\"(?P<ownerID2>\d+)\" argName1=\"(?P<argName1>.*?)\" argID1=\"(?P<argID1>\d+)\" amount=\"(?P<amount>\d+\.\d\d)\" balance=\"(?P<balance>\d+\.\d\d)\" reason=\"(?P<reason>.*?)\" taxReceiverID=\"(?P<taxReceiverID>\d+)\" taxAmount=\"(?P<taxAmount>\d+\.\d\d)\" \/\>", xml)
            refTypes = self.Eve("reftypes")
            
            while True:
                try:
                    row = rows.next().groupdict()
                except StopIteration:
                    break
                    
                else:
                    walletdict[int(row["refID"])] = {
                        "refID" : int(row["refID"]),
                        "refTypeID" : int(row["refTypeID"]),
                        "refTypeName" : refTypes[int(row["refTypeID"])],
                        "date" : time.mktime(time.strptime(row["date"], "%Y-%m-%d %H:%M:%S")),
                        "amount" : float(row["amount"]),
                        "taxAmount" : float(row["taxAmount"]),
                        "taxReceiverID" : int(row["taxReceiverID"]),
                        "taxReceiverName" : self.Eve("getname",nameID=int(row["taxReceiverID"]))["Name"],
                        "ownerID1" : int(row["ownerID1"]),
                        "ownerName1" : row["ownerName1"],
                        "ownerID2" : int(row["ownerID2"]),
                        "ownerName2" : row["ownerName2"],
                        "argID1" : int(row["argID1"]),
                        "argName1" : row["argName1"],
                        "reason" : row["reason"],
                        "balance" : row["balance"],
                    }
                    if int(row["refTypeID"]) == 85:
                        reason = row["reason"]
                        elements = reason.split(",")
                        kills = []
                        for element in elements:
                            if element != "":
                                NPCid = int(element.split(":")[0])
                                NPCName = self.Eve("getname", nameID=NPCid)["Name"]
                                count = int(element.split(":")[1])
                                kills += [{
                                    "shipID" : NPCid,
                                    "shipName" : NPCName,
                                    "count" : count
                                }]
                        walletdict[int(row["refID"])]["_kills_"] = kills
            return walletdict

        elif Request.lower() == "transacts":
            requesturl = os.path.join(self.API_URL, "char/WalletTransactions.xml.aspx")
            xml = self._getXML(requesturl, basepostdata)
            print xml
            #1000 results
            #can use beforeTransID=TransID to see more

    def Account(self, Request):
        """ Methods related to an account:
            **********************************************
            characters : returns a list of characters (L)
            status : account status (F)
            **********************************************
            (L) = limited API key required
            (F) = full API key required
        """

        if Request.lower() == "characters":
            requesturl = os.path.join(self.API_URL, "account/Characters.xml.aspx")
            postdata = {
                "apiKey" : self.API_KEY,
                "userID" : self.USER_ID
            }
            xml = self._getXML(requesturl, postdata)

            #parse xml
            result = xml.split("<result>")[1].split("</result>")[0]
            splitline = re.search("(\<rowset.*?\>)", result).group(1)
            result = result.split(splitline)[1].split("</rowset>")[0].strip()
            rows = [x.strip() for x in result.split("<row")[1:]]
            chardict = {}
            for row in rows:
                if self.DEBUG:
                    print row
                name = ""
                value = ""
                NAME = True
                VALUE = False
                STRING = False
                tempdict = {}
                for char in row:
                    if char == "=" and not STRING:
                        if NAME:
                            if self.DEBUG:
                                print "name:",name
                            NAME = False
                            VALUE = True
                            STRING = False
                    elif char == "\"":
                        if STRING:
                            STRING = False
                        else:
                            STRING = True
                    elif char == " " and not STRING:
                        if not NAME:
                            if self.DEBUG:
                                print "value:",value
                            NAME = True
                            VALUE = False
                            STRING = False
                            if value[0] == "\"" or value[0] == "'":
                                value = value[1:-1]
                            else:
                                try:
                                    if "." in value:
                                        value = float(value)
                                    else:
                                        value = int(value)
                                except:
                                    pass
                            tempdict[name] = value
                            name = ""
                            value = ""

                    if char == " " and not STRING:
                        pass
                    elif char == "=" and not STRING:
                        pass
                    else:
                        if NAME:
                            name += char
                        elif VALUE:
                            value += char
                chardict[tempdict["name"]] = tempdict
            return chardict
        elif Request.lower() == "status":
            requesturl = os.path.join(self.API_URL, "account/AccountStatus.xml.aspx")
            postdata = {
                "apiKey" : self.API_KEY,
                "userID" : self.USER_ID
            }
            xml = self._getXML(requesturl, postdata)
            result = xml.split("<result>")[1].split("</result>")[0].strip()
            def getTag(tag):
                return result.split("<%s>" % tag)[1].split("</%s>" % tag)[0].strip()
            createDate = getTag("createDate")
            paidUntil = getTag("paidUntil")
            logonCount = int(getTag("logonCount"))
            logonMinutes = int(getTag("logonMinutes"))

            createDate_unix = time.mktime(time.strptime(createDate, "%Y-%m-%d %H:%M:%S"))
            paidUntil_unix = time.mktime(time.strptime(paidUntil, "%Y-%m-%d %H:%M:%S"))
            #logged_on = ""
            #if logonMinutes >= 10080:
            #    weeks = logonMinutes / 10080
            #    logged_on += "%i weeks " % weeks
            #    logonMinutes -= weeks * 10080
            #if logonMinutes >= 1440:
            #    days = logonMinutes / 1440
            #    logged_on += "%i days " % days
            #    logonMinutes -= days * 1440
            #if logonMinutes >= 60:
            #    hours = logonMinutes / 60
            #    logged_on += "%i hours " % hours
            #    logonMinutes -= hours * 60
            #logged_on += "%i minutes" % logonMinutes

            return {
                "createDate" : createDate_unix,
                "paidUntil" : paidUntil_unix,
                "logonCount" : logonCount,
                "logonMinutes" : logonMinutes
            }
    def Map(self, Request, systemname):
        """ Methods related to systems:
            ************************************************
            jumps : number of jumps into a specified system (N)
            kills : number of ship and pod kills in a specified system (N)
            sov : system sovereignty information (N)
            ************************************************
            (N) = no API key required
        """
        if Request.lower() == "jumps":
            requesturl = os.path.join(self.API_URL, "map/Jumps.xml.aspx")
            xml = self._getXML(requesturl)
            print xml

        if Request.lower() == "kills":
            solarSystemID_str = self.EVE.getSystemIDByName(systemname)
            if solarSystemID_str:
                requesturl = os.path.join(self.API_URL, "map/Kills.xml.aspx")
                xml = self._getXML(requesturl)
                solarSystemID = int(solarSystemID_str)
                try:
                    shipKills, factionKills, podKills = re.findall("\<row solarSystemID=\"%i\" shipKills=\"(\d+)\" factionKills=\"(\d+)\" podKills=\"(\d+)\" \/\>" % (solarSystemID), xml)[0]
                except IndexError:
                    return {
                        "solarSystemID" : solarSystemID,
                        "solarSystemName" : self.EVE.getSystemNameByID(solarSystemID),
                        "shipKills" : 0,
                        "podKills" : 0,
                        "npcKills" : 0
                    }
                else:
                    return {
                        "solarSystemID" : solarSystemID,
                        "solarSystemName" : self.EVE.getSystemNameByID(solarSystemID),
                        "shipKills" : int(shipKills),
                        "podKills" : int(podKills),
                        "npcKills" : int(factionKills)
                    }

        if Request.lower() == "sov":
            solarSystemID_str = self.EVE.getSystemIDByName(systemname.upper())
            if solarSystemID_str:
                requesturl = os.path.join(self.API_URL, "map/Sovereignty.xml.aspx")
                xml = self._getXML(requesturl)
                solarSystemID = int(solarSystemID_str)
                try:
                    allianceID, factionID, solarSystemName, corporationID = re.findall("\<row solarSystemID=\"%i\" allianceID=\"(\d+)\" factionID=\"(\d+)\" solarSystemName=\"(.*?)\" corporationID=\"(\d+)\" \/\>" % (solarSystemID), xml)[0]
                except IndexError:
                    return None
                else:
                    if allianceID != "0" and corporationID != "0":
                        corporationName = self.Corporation("publicsheet", corporationID)["corporationName"]
                        allianceInfo = self.Eve("alliances", int(allianceID))
                        allianceName = allianceInfo["allianceName"]
                        allianceTicker = allianceInfo["allianceTicker"]
                        return {
                            "solarSystemID" : int(solarSystemID),
                            "solarSystemName" : solarSystemName,
                            "allianceID" : int(allianceID),
                            "allianceName" : allianceName,
                            "allianceTicker" : allianceTicker,
                            "factionID" : None,
                            "factionName" : None,
                            "corporationID" : int(corporationID),
                            "corporationName" : corporationName
                        }
                    else:
                        factionName = self.EVE.getFactionNameByID(factionID)
                        return {
                            "solarSystemID" : int(solarSystemID),
                            "solarSystemName" : solarSystemName,
                            "allianceID" : None,
                            "allianceName" : None,
                            "allianceTicker" : None,
                            "factionID" : int(factionID),
                            "factionName" : factionName,
                            "corporationID" : None,
                            "corporationName" : None
                        }

    def Server(self, Request):
        """ Methods related to the server:
            ************************************************
            status : server status (N)
            ************************************************
            (N) = no API key required
        """

        if Request.lower() == "status":
            requesturl = os.path.join(self.API_URL, "server/ServerStatus.xml.aspx")
            xml = urllib2.urlopen(requesturl).read()
            status = re.search("\<serverOpen\>(.*?)\<\/serverOpen\>", xml).group(1)
            if status == "True":
                status = "Online"
            else:
                status = "Offline"
            online = int(re.search("\<onlinePlayers\>(\d+)\<\/onlinePlayers\>", xml).group(1))
            return {
                "status" : status,
                "online" : online
            }

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
    
    def Eve(self,Request, allianceID=None, characterID=None, allianceName=None, allianceTicker=None):
        """
            Methods related to EVE in general:
            *********************************************
            alliances : returns alliance info for a given
                        allianceID, allianceName or allianceID(N)
                        # currently outputs only allianceID, 
                        # allianceName and allianceTicker
            characterName : returns the characterName for a given characterID
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
                    allianceID, allName, allianceTicker = re.findall("\<row=\"(%s)\" shortName=\"(.*?)\" allianceID=\"(\d+)\"" % (allianceName), xml, re.I)[0]
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
                    allianceID, allianceName, Ticker = re.findall("\<row=\"(.*?)\" shortName=\"(%s)\" allianceID+\"(\d+)\"" % (allianceTicker), xml, re.I)[0]
                except IndexError:
                    return None
                else:
                    return {
                        "allianceID" : int(allianceID),
                        "allianceName" : allianceName,
                        "alliaceTicker" : Ticker
                    }
            else:
                return None
        elif Request.lower() == "charactername":
            requesturl = os.path.join(self.API_URL, "eve/CharacterName.xml.aspx")
            postdata = {
                "ids" : characterID
            }
            if characterID:
                xml = self._getXML(requesturl, postdata)
                try:
                    charName, charID = re.findall("\<row name=\"(.*?)\" characterID=\"(\d+)\" \/\>", xml)[0]
                except IndexError:
                    return None
                else:
                    return {
                        "characterName" : charName,
                        "characterID" : int(charID)
                    }            
            
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
                
                #for now, just return corporationName
                return {
                    "corporationName" : corporationName
                }
            else:
                return None
            
#  <result>
#    <corporationID>1102238026</corporationID>
#    <corporationName>LazyBoyz Band of Recreational Flyers</corporationName>
#    <ticker>LBBRF</ticker>
#    <ceoID>2081077519</ceoID>
#    <ceoName>Gheent</ceoName>
#    <stationID>60005086</stationID>
#    <stationName>Alakgur VII - Moon 3 - Republic Security Services Assembly Plant</stationName>
#    <description>Players of all skill levels are welcomed into a friendly Corp.&lt;br&gt;&lt;br&gt;Our Corp is growing in all aspects of the game, beside our regular mission and mining ops, wormhole exploration and the occasionaly pvp sessions. We also do lots of research and manufacturing, at our own highsec and nullsec POS's!&lt;br&gt;&lt;br&gt;Furthermore we are proud to be part of the [Intergalactic Exports Group] Alliance and are currently active in 0.0 space. Don't let it scare you off, since we have a strong base of operations down in secure nullsec space for any newcomers to the game!&lt;br&gt;&lt;br&gt;This could be your window of opportunity and let it be known that &lt;a href="showinfo:2//1102238026"&gt;Lazyboyz Band of Recreational Flyers&lt;/a&gt; will aid you in anyway we can to get you to roam amongst the stars.&lt;br&gt;&lt;br&gt;We host no obligations, and there is no risk of getting kicked out, your attendence is not required, but of course as we are all friends, we love to see you show up. In this family we totally understanding that real life obligations should come before those of EVE&lt;br&gt;&lt;br&gt;Corp tax is currently maintained at 8%, this is due to Corp expenses joining our alliance in null-sec, and to pay the rent for our own systems. We have financial support for the newcomers</description>
#    <url>http://www.eveonline.com</url>
#    <allianceID>1076729448</allianceID>
#    <allianceName>Intergalactic Exports Group</allianceName>
#    <taxRate>8</taxRate>
#    <memberCount>61</memberCount>
#    <shares>101000</shares>
#    <logo>
#      <graphicID>0</graphicID>
#      <shape1>439</shape1>
#      <shape2>451</shape2>
#      <shape3>513</shape3>
#      <color1>677</color1>
#      <color2>679</color2>
#      <color3>680</color3>
#    </logo>
#  </result>
#  <cachedUntil>2011-01-21 23:28:01</cachedUntil>
#</eveapi>

            
    def Char(self, Request, mailID=None):
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
                            allianceCheck = self.Eve("alliances", tCOAID)
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
                                charCheck = self.Eve("characterName", characterID=charID)
                                if charCheck:
                                    charName = charCheck["characterName"]
                                    toCharDict[charID] = {"characterName" : charName}
                                
                        maildict[int(row["messageID"])] = {
                            "senderID" : int(row["senderID"]),
                            "senderName" : self.Eve("characterName", characterID=int(row["senderID"]))["characterName"],
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
            
#<?xml version='1.0' encoding='UTF-8'?>
#<eveapi version="2">
#  <currentTime>2011-01-24 22:43:06</currentTime>
#  <result>
#    <rowset name="skillqueue" key="queuePosition" columns="queuePosition,typeID,level,startSP,endSP,startTime,endTime">
#      <row queuePosition="0" typeID="30546" level="5" startSP="45255" endSP="256000" startTime="2011-01-22 20:25:45" endTime="2011-01-26 18:05:37" />
#    </rowset>
#  </result>
#  <cachedUntil>2011-01-24 23:40:06</cachedUntil>
#</eveapi>

            #regex = self.XML.getDefaultRegex(xml)[0]
            #return regex.search(xml).groupdict()

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

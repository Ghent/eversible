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
"""

import sqlite3
from modules import api
import random
import string
import hashlib
import traceback
import time

class DB:
    def __init__(self):
        self.conn = sqlite3.connect("var/users/eversible.db")
        self.cursor = self.conn.cursor()
        #test if users / hostnames tables exist
        try:
            self.cursor.execute("""
                           CREATE TABLE users
                           (id text, characterName text, characterID integer, keyID integer, vCode text, password text)
                           """)
        except sqlite3.OperationalError:
            pass
        
        try:
            self.cursor.execute("""
                           CREATE TABLE hostnames
                           (id text, hostname text)
                           """)
        except sqlite3.OperationalError:
            pass
    
    def getMessageID(self, charID):
      
        try:
            self.cursor.execute("""
                           SELECT messageID, sentTime
                           FROM mail
                           WHERE charID=?
                           """, (charID,))
        except sqlite3.OperationalError:
            return None
        else:
            result = self.cursor.fetchone()
            if result:
                return (int(result[0]), float(result[1]))
            else:
                return None
            
    def insertMessageID(self, charID, messageID, sentTime):
        try:
            self.cursor.execute("""
                           CREATE TABLE mail
                           (charID integer, messageID integer, sentTime real)
                           """)
        except sqlite3.OperationalError:
            pass
        else:
            self.conn.commit()
            
        #remove old entry
        self.cursor.execute("""
                       DELETE FROM mail
                       WHERE charID=?
                       """, (charID,))
        
        self.cursor.execute("""
                       INSERT INTO mail
                       (charID, messageID, sentTime)
                       VALUES (?, ?, ?)
                       """, (charID, messageID, sentTime)
                      )
        
        self.conn.commit()
        
    def getHostnames(self):
        #this fails if database not initialised
        
        self.cursor.execute("""
                       SELECT id, hostname
                       FROM hostnames
                       """)
        
        results = self.cursor.fetchall()
        
        return dict(results)

    def createUser(self, keyID, vCode, characterName, password, hostname, hashpassword=None):
        try:
            API = api.API(keyID=keyID, vCode=vCode, characterName=characterName)
        except api.APIError as error:
            return (False, error)
        else:
            if API.CHAR_ID:
                characters = API.Account("characters")
                if not hashpassword:
                    hashpassword = hashlib.md5(password).hexdigest()
                randomid = "".join([
                    random.choice(string.ascii_letters + string.digits) for x in range(20)
                ])
                
                #first check if user exists
                def alreadyexists(characterName, keyID):
                    self.cursor.execute("""
                                   SELECT id,characterName,keyID
                                   FROM users
                                   WHERE characterName = ?
                                   """, (characterName,)
                                  )
                    check = self.cursor.fetchone()
                    if check:
                        return (False, 'Entry already exists')
                    else:
                        return (True, '')
                        
                response = alreadyexists(characterName, keyID)
                if not response[0]:
                    return response
                
                self.cursor.execute("""
                               INSERT INTO users
                               (id, characterName, characterID, keyID, vCode, password)
                               VALUES (?, ?, ?, ?, ?, ?)
                               """, (randomid, characterName, API.CHAR_ID, keyID, vCode, hashpassword)
                              )
                
                #add alternate characters also
                for characterName_alt in characters.keys():
                    if alreadyexists(characterName_alt, keyID)[0]:
                        randomid_alt = "".join([random.choice(string.ascii_letters + string.digits) for x in range(20)])
                        charID_alt = characters[characterName_alt]["characterID"]
                        
                        self.cursor.execute("""
                                       INSERT INTO users
                                       (id, characterName, characterID, keyID, vCode, password)
                                       VALUES (?, ?, ?, ?, ?, ?)
                                       """,(randomid_alt, characterName_alt, charID_alt, keyID, vCode, hashpassword)
                                      )
                        
                self.removeHostname(hostname)
                
                self.cursor.execute("""
                               INSERT INTO hostnames
                               (id, hostname)
                               VALUES (?, ?)
                               """, (randomid, hostname)
                              )
                self.conn.commit()
                return (True,'')
            else:
                return (False,'Invalid details')
            
    def lookForAlts(self, vCode, keyID):
        try:
            self.cursor.execute("""
                           SELECT characterName
                           FROM users
                           WHERE vCode=?
                           AND keyID=?
                           """, (vCode, keyID)
                          )
        except sqlite3.OperationalError:
            return None
        else:
            results = self.cursor.fetchall()
            return results
        
    def lookupAlt(self, vCode, keyID, characterName, altName):
        API = api.API(keyID=keyID, vCode=vCode)
        characters = API.Account("characters")
        if characterName in characters.keys() and altName in characters.keys():
            try:
                self.cursor.execute("""
                               SELECT id, characterName, characterID, keyID, vCode
                               FROM users
                               WHERE characterName=?
                               AND keyID=?
                               AND vCode=?
                               """, (altName, keyID, vCode)
                              )
            except sqlite3.OperationalError:
                return None
            else:
                result = self.cursor.fetchone()
                if not result:
                    return None
                else:
                    return True
        else:
            return None
    
    def retrieveUserByHostname(self, hostname):
        try:
            self.cursor.execute("""
                           SELECT id, hostname
                           FROM hostnames
                           WHERE hostname=?
                           """, (hostname,))
            
        except sqlite3.OperationalError:
            return None
        else:
            result = self.cursor.fetchone()
            if result:
                user_id = result[0]
            else:
                return None
            
            try:
            
                self.cursor.execute("""
                               SELECT id, characterName, characterID, keyID, vCode
                               FROM users
                               WHERE id=?
                               """, (user_id,)
                              )
            except sqlite3.OperationalError:
                return None
            else:
                result = self.cursor.fetchone()
                if result:
                    return {
                        "characterName" : result[1],
                        "characterID" : result[2],
                        "keyID" : result[3],
                        "vCode" : result[4],
                        "apiObject" : api.API(keyID=result[3], vCode=result[4], charid=result[2], characterName=result[1])
                    }
                else:
                    return None
    
    def removeHostnameByNick(self, nick):
        try:
            self.cursor.execute("""
                           DELETE
                           FROM hostnames
                           WHERE glob("%s!*",hostname)
                           """, (nick,))
        except sqlite3.OperationalError:
            pass
        self.conn.commit()
        
    def updateUser(self, characterName, keyID, new_vCode, hostname):
        try:
            #id, characterName, characterID, keyID, vCode, password
            self.cursor.execute("""
                           SELECT id, characterName, keyID, vCode, password
                           FROM users
                           WHERE
                           characterName=?
                           """, (characterName,)
                          )
        except sqlite3.OperationalError:
            return (False, "Database couldn't be found")
        else:
            result = self.cursor.fetchone()
            if not result:
                return (False, "Incorrect characterName or password")
            
            #get alts
            alts = self.lookForAlts(result[3], result[2])
            for altName in alts:
                try:
                    self.cursor.execute("""
                                   DELETE
                                   FROM users
                                   WHERE characterName = ?
                                   """, (altName[0],)
                                  )
                except sqlite3.OperationalError:
                    traceback.print_exc()
            self.conn.commit()
            response = self.createUser(keyID, new_vCode, characterName, None, hostname, hashpassword=result[4])
            return response
                
    def removeHostname(self, hostname):
        try:
            self.cursor.execute("""
                           DELETE
                           FROM hostnames
                           WHERE hostname=?
                           """, (hostname,))
        except sqlite3.OperationalError:
            pass
        self.conn.commit()
        
    def verifyPassword(self, characterName, password):
        hashpassword = hashlib.md5(password).hexdigest()
        try:
            self.cursor.execute("""
                           SELECT id, characterName, password
                           FROM users
                           WHERE
                           characterName=? AND password=?
                           """, (characterName, hashpassword)
                          )
        except sqlite3.OperationalError:
            return False
        else:
            if self.cursor.fetchone():
                return True
            else:
                return False
        
    def testIdentity(self, characterName, password, hostname):
        hashpassword = hashlib.md5(password).hexdigest()
        try:
            self.cursor.execute("""
                           SELECT id, characterName, password
                           FROM users
                           WHERE
                           characterName=? AND password=?
                           """, (characterName, hashpassword)
                          )
        except sqlite3.OperationalError:
            return False
        else:
            result = self.cursor.fetchone()
            if result:
                #insert hostname into hostnames table
                self.removeHostname(hostname)
                id = result[0]
                self.cursor.execute("""
                               INSERT INTO hostnames
                               (id, hostname)
                               VALUES (?, ?)
                               """, (id, hostname)
                              )
                self.conn.commit()
                return True
            else:
                return False
            
    def addHostname(self, characterName, hostname):
        #get associated id
        self.cursor.execute("""
                       SELECT id,characterName
                       FROM users
                       WHERE characterName=?
                       """, (characterName,))
        result = self.cursor.fetchone()
        
        if not result:
            return False
        else:
            self.removeHostname(hostname)
            
            self.cursor.execute("""
                           INSERT INTO hostnames
                           (id, hostname)
                           VALUES (?, ?)
                           """, (result[0], hostname)
                          )
            self.conn.commit()
            return True

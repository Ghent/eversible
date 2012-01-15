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
        conn = sqlite3.connect("var/users/eversible.db")
        cursor = conn.cursor()
        #test if users / hostnames tables exist
        try:
            cursor.execute("""
                           CREATE TABLE users
                           (id text, characterName text, characterID integer, keyID integer, vCode text, password text)
                           """)
        except sqlite3.OperationalError:
            pass
        
        try:
            cursor.execute("""
                           CREATE TABLE hostnames
                           (id text, hostname text)
                           """)
        except sqlite3.OperationalError:
            pass
    
    def getMessageID(self, charID):
        conn = sqlite3.connect("var/users/eversible.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                           SELECT messageID, sentTime
                           FROM mail
                           WHERE charID=?
                           """, (charID,))
        except sqlite3.OperationalError:
            return None
        else:
            result = cursor.fetchone()
            if result:
                return (int(result[0]), float(result[1]))
            else:
                return None
            
    def insertMessageID(self, charID, messageID, sentTime):
        conn = sqlite3.connect("var/users/eversible.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                           CREATE TABLE mail
                           (charID integer, messageID integer, sentTime real)
                           """)
        except sqlite3.OperationalError:
            pass
        else:
            conn.commit()
            
        #remove old entry
        cursor.execute("""
                       DELETE FROM mail
                       WHERE charID=?
                       """, (charID,))
        
        cursor.execute("""
                       INSERT INTO mail
                       (charID, messageID, sentTime)
                       VALUES (?, ?, ?)
                       """, (charID, messageID, sentTime)
                      )
        
        conn.commit()
        cursor.close()
        conn.close()
        
    def getHostnames(self):
        conn = sqlite3.connect("var/users/eversible.db")
        cursor = conn.cursor()

        #this fails if database not initialised
        
        cursor.execute("""
                       SELECT id, hostname
                       FROM hostnames
                       """)
        
        results = cursor.fetchall()
        cursor.close()
        conn.close()
        
        return dict(results)

    def createUser(self, keyID, vCode, characterName, password, hostname, hashpassword=None):
        API = api.API(keyID=keyID, vCode=vCode, characterName=characterName)
        if API.CHAR_ID:
            characters = API.Account("characters")
            if not hashpassword:
                hashpassword = hashlib.md5(password).hexdigest()
            conn = sqlite3.connect("var/users/eversible.db")
            cursor = conn.cursor()
            
            randomid = "".join([
                random.choice(string.ascii_letters + string.digits) for x in range(20)
            ])
            
            #first check if user exists
            def alreadyexists(characterName, keyID):
                cursor.execute("""
                               SELECT id,characterName,keyID
                               FROM users
                               WHERE characterName = ?
                               AND keyID = ?
                               """, (characterName, keyID)
                              )
                check = cursor.fetchone()
                if check:
                    return (False, 'Entry already exists')
                else:
                    return (True, '')
                    
            response = alreadyexists(characterName, keyID)
            if not response[0]:
                return response
            
            cursor.execute("""
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
                    
                    cursor.execute("""
                                   INSERT INTO users
                                   (id, characterName, characterID, keyID, vCode, password)
                                   VALUES (?, ?, ?, ?, ?, ?)
                                   """,(randomid_alt, characterName_alt, charID_alt, keyID, vCode, hashpassword)
                                  )
                    
            self.removeHostname(hostname)
            
            cursor.execute("""
                           INSERT INTO hostnames
                           (id, hostname)
                           VALUES (?, ?)
                           """, (randomid, hostname)
                          )
            conn.commit()
            cursor.close()
            conn.close()
            return (True,'')
        else:
            return (False,'Invalid details')
            
    def lookForAlts(self, vCode, keyID):
        conn = sqlite3.connect("var/users/eversible.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           SELECT characterName
                           FROM users
                           WHERE vCode=?
                           AND keyID=?
                           """, (vCode, keyID)
                          )
        except sqlite3.OperationalError:
            cursor.close()
            conn.close()
            return None
        else:
            results = cursor.fetchall()
            cursor.close()
            conn.close()
            return results
        
    def lookupAlt(self, vCode, keyID, characterName, altName):
        API = api.API(keyID=keyID, vCode=vCode)
        characters = API.Account("characters")
        if characterName in characters.keys() and altName in characters.keys():
            conn = sqlite3.connect("var/users/eversible.db")
            cursor = conn.cursor()
            try:
                cursor.execute("""
                               SELECT id, characterName, characterID, keyID, vCode
                               FROM users
                               WHERE characterName=?
                               AND keyID=?
                               AND vCode=?
                               """, (altName, keyID, vCode)
                              )
            except sqlite3.OperationalError:
                cursor.close()
                conn.close()
                return None
            else:
                result = cursor.fetchone()
                if not result:
                    cursor.close()
                    conn.close()
                    return None
                else:
                    cursor.close()
                    conn.close()
                    return True
        else:
            return None
    
    def retrieveUserByHostname(self, hostname):
        conn = sqlite3.connect("var/users/eversible.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           SELECT id, hostname
                           FROM hostnames
                           WHERE hostname=?
                           """, (hostname,))
            
        except sqlite3.OperationalError:
            cursor.close()
            conn.close()
            return None
        else:
            result = cursor.fetchone()
            if result:
                user_id = result[0]
            else:
                cursor.close()
                conn.close()
                return None
            
            try:
            
                cursor.execute("""
                               SELECT id, characterName, characterID, keyID, vCode
                               FROM users
                               WHERE id=?
                               """, (user_id,)
                              )
            except sqlite3.OperationalError:
                cursor.close()
                conn.close()
                return None
            else:
                result = cursor.fetchone()
                cursor.close()
                conn.close()
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
        cursor.close()
        conn.close()
    
    def removeHostnameByNick(self, nick):
        conn = sqlite3.connect("var/users/eversible.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           DELETE
                           FROM hostnames
                           WHERE glob("%s!*",hostname)
                           """, (nick,))
        except sqlite3.OperationalError:
            pass
        conn.commit()
        cursor.close()
        conn.close()
        
    def updateUser(self, characterName, keyID, new_vCode, hostname):
        conn = sqlite3.connect("var/users/eversible.db")
        cursor = conn.cursor()
        try:
            #id, characterName, characterID, keyID, vCode, password
            cursor.execute("""
                           SELECT id, characterName, keyID, vCode, password
                           FROM users
                           WHERE
                           characterName=?
                           """, (characterName,)
                          )
        except sqlite3.OperationalError:
            cursor.close()
            conn.close()
            return (False, "Database couldn't be found")
        else:
            result = cursor.fetchone()
            if not result:
                cursor.close()
                conn.close()
                return (False, "Incorrect characterName or password")
            
            #get alts
            alts = self.lookForAlts(result[3], result[2])
            for altName in alts:
                try:
                    cursor.execute("""
                                   DELETE
                                   FROM users
                                   WHERE characterName = ?
                                   """, (altName[0],)
                                  )
                except sqlite3.OperationalError:
                    traceback.print_exc()
            conn.commit()
            response = self.createUser(keyID, new_vCode, characterName, None, hostname, hashpassword=result[4])
            cursor.close()
            conn.close()
            return response
                
    def removeHostname(self, hostname):
        conn = sqlite3.connect("var/users/eversible.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           DELETE
                           FROM hostnames
                           WHERE hostname=?
                           """, (hostname,))
        except sqlite3.OperationalError:
            pass
        conn.commit()
        cursor.close()
        conn.close()
        
    def verifyPassword(self, characterName, password):
        conn = sqlite3.connect("var/users/eversible.db")
        cursor = conn.cursor()
        hashpassword = hashlib.md5(password).hexdigest()
        try:
            cursor.execute("""
                           SELECT id, characterName, password
                           FROM users
                           WHERE
                           characterName=? AND password=?
                           """, (characterName, hashpassword)
                          )
        except sqlite3.OperationalError:
            cursor.close()
            conn.close()
            return False
        else:
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return True
            else:
                cursor.close()
                conn.close()
                return False
        
    def testIdentity(self, characterName, password, hostname):
        conn = sqlite3.connect("var/users/eversible.db")
        cursor = conn.cursor()
        hashpassword = hashlib.md5(password).hexdigest()
        try:
            cursor.execute("""
                           SELECT id, characterName, password
                           FROM users
                           WHERE
                           characterName=? AND password=?
                           """, (characterName, hashpassword)
                          )
        except sqlite3.OperationalError:
            cursor.close()
            conn.close()
            return False
        else:
            result = cursor.fetchone()
            if result:
                #insert hostname into hostnames table
                self.removeHostname(hostname)
                id = result[0]
                cursor.execute("""
                               INSERT INTO hostnames
                               (id, hostname)
                               VALUES (?, ?)
                               """, (id, hostname)
                              )
                conn.commit()
                cursor.close()
                conn.close()
                return True
            else:
                cursor.close()
                conn.close()
                return False
            
    def addHostname(self, characterName, hostname):
        conn = sqlite3.connect("var/users/eversible.db")
        cursor = conn.cursor()
        
        #get associated id
        cursor.execute("""
                       SELECT id,characterName
                       FROM users
                       WHERE characterName=?
                       """, (characterName,))
        result = cursor.fetchone()
        
        if not result:
            cursor.close()
            conn.close()
            return False
        else:
            self.removeHostname(hostname)
            
            cursor.execute("""
                           INSERT INTO hostnames
                           (id, hostname)
                           VALUES (?, ?)
                           """, (result[0], hostname)
                          )
            conn.commit()
            cursor.close()
            conn.close()
            return True

#!/usr/bin/env python

import sqlite3
import api
import random
import string
import md5

class DB:
    def __init__(self):
        pass
    
    def _dropDB(self):
        """For debugging purposes"""
        conn = sqlite3.connect("users/eversible.db")
        cursor = conn.cursor()
        cursor.execute("DROP TABLE hostnames")
        cursor.execute("DROP TABLE users")
        cursor.close()
        conn.close()

    def createUser(self, apiKey, userID, characterName, password, hostname):
        API = api.API(apikey=apiKey, userid=userID, charid=None)
        characters = API.Account("characters")
        hashpassword = md5.new(password).hexdigest()

        if characterName in characters.keys():
            charID = characters[characterName]["characterID"]
            conn = sqlite3.connect("users/eversible.db")
            cursor = conn.cursor()
            try:
                cursor.execute("""
                               CREATE TABLE users
                               (id text, characterName text, characterID integer, userID integer, apiKey text, password text)
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
            
            randomid = "".join([
                random.choice(string.ascii_letters + string.digits) for x in range(20)
            ])
            
            #first check if user exists
            cursor.execute("""
                           SELECT id,characterName,userID
                           FROM users
                           WHERE characterName="%s"
                           AND userID = "%s"
                           """ % (characterName, userID)
                          )
            check = cursor.fetchone()
            if check:
                return (False, 'Entry already exists')
            
            cursor.execute("""
                           INSERT INTO users
                           (id, characterName, characterID, userID, apiKey, password)
                           VALUES ("%s", "%s", "%s", "%s", "%s", "%s")
                           """ % (randomid, characterName, charID, userID, apiKey, hashpassword)
                          )
            
            self.removeHostname(hostname)
            
            cursor.execute("""
                           INSERT INTO hostnames
                           (id, hostname)
                           VALUES ("%s", "%s")
                           """ % (randomid, hostname)
                          )
            conn.commit()
            cursor.close()
            conn.close()
            return (True,'')
        else:
            return (False,'Invalid details')
            
    def lookForAlts(self, apiKey, userID):
        conn = sqlite3.connect("users/eversible.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           SELECT characterName
                           FROM users
                           WHERE apiKey="%s"
                           AND userID="%s"
                           """ % (apiKey, userID)
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
    def lookupAlt(self, apiKey, userID, characterName, altName):
        API = api.API(apikey=apiKey, userid=userID)
        characters = API.Account("characters")
        if characterName in characters.keys() and altName in characters.keys():
            conn = sqlite3.connect("users/eversible.db")
            cursor = conn.cursor()
            try:
                cursor.execute("""
                               SELECT id, characterName, characterID, userID, apiKey
                               FROM users
                               WHERE characterName='%s'
                               AND userID='%s'
                               AND apiKey='%s'
                               """ % (altName, userID, apiKey)
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
        conn = sqlite3.connect("users/eversible.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           SELECT id, hostname
                           FROM hostnames
                           WHERE hostname="%s"
                           """ % (hostname))
            
        except sqlite3.OperationalError:
            cursor.close()
            conn.close()
            return None
        else:
            result = cursor.fetchone()
            if result:
                print result
                user_id = result[0]
                print user_id
            else:
                cursor.close()
                conn.close()
                return None
            
            try:
            
                cursor.execute("""
                               SELECT id, characterName, characterID, userID, apiKey
                               FROM users
                               WHERE id="%s"
                               """ % (user_id)
                              )
            except sqlite3.OperationalError:
                cursor.close()
                conn.close()
                return None
            else:
                result = cursor.fetchone()
                cursor.close()
                conn.close()
                return {
                    "characterName" : result[1],
                    "characterID" : result[2],
                    "userID" : result[3],
                    "apiKey" : result[4]
                }
        cursor.close()
        conn.close()
    
    def removeHostnameByNick(self, nick):
        conn = sqlite3.connect("users/eversible.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           DELETE
                           FROM hostnames
                           WHERE glob("%s!*",hostname)
                           """ % nick)
        except sqlite3.OperationalError:
            pass
        conn.commit()
        cursor.close()
        conn.close()
        
    def removeHostname(self, hostname):
        conn = sqlite3.connect("users/eversible.db")
        cursor = conn.cursor()
        try:
            cursor.execute("""
                           DELETE
                           FROM hostnames
                           WHERE hostname="%s"
                           """ % hostname)
        except sqlite3.OperationalError:
            pass
        conn.commit()
        cursor.close()
        conn.close()
        
    def testIdentity(self, characterName, password, hostname):
        conn = sqlite3.connect("users/eversible.db")
        cursor = conn.cursor()
        hashpassword = md5.new(password).hexdigest()
        try:
            cursor.execute("""
                           SELECT id, characterName, password
                           FROM users
                           WHERE
                           characterName="%s" AND password="%s"
                           """ % (characterName, hashpassword)
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
                               VALUES ("%s", "%s")
                               """ % (id, hostname)
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
        conn = sqlite3.connect("users/eversible.db")
        cursor = conn.cursor()
        
        #get associated id
        cursor.execute("""
                       SELECT id,characterName,apiKey,userID
                       FROM users
                       WHERE characterName="%s"
                       """ % characterName)
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
                           VALUES ("%s", "%s")
                           """ % (result[0], hostname)
                          )
            conn.commit()
            cursor.close()
            conn.close()
            return True
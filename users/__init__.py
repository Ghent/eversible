#!/usr/bin/env python

import sqlite3
import api
import random
import string
import hashlib
import traceback

class DB:
    def __init__(self):
        pass
    
    def getMessageID(self, charID):
        conn = sqlite3.connect("users/eversible.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                           SELECT messageID, sentTime
                           FROM mail
                           WHERE charID="%s"
                           """ % charID)
        except sqlite3.OperationalError:
            return None
        else:
            result = cursor.fetchone()
            if result:
                return (int(result[0]), float(result[1]))
            else:
                return None
            
    def insertMessageID(self, charID, messageID, sentTime):
        conn = sqlite3.connect("users/eversible.db")
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
                       WHERE charID="%s"
                       """ % charID)
        
        cursor.execute("""
                       INSERT INTO mail
                       (charID, messageID, sentTime)
                       VALUES ("%s","%s", "%s")
                       """ % (charID, messageID, sentTime)
                      )
        
        conn.commit()
        cursor.close()
        conn.close()
        
    def getHostnames(self):
        conn = sqlite3.connect("users/eversible.db")
        cursor = conn.cursor()
        
        cursor.execute("""
                       SELECT id, hostname
                       FROM hostnames
                       """)
        
        results = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        result_dict = {}
        for result in results:
            result_dict[result[0]] = result[1]
            
        return result_dict

    def createUser(self, apiKey, userID, characterName, password, hostname):
        API = api.API(apikey=apiKey, userid=userID, charid=None)
        try:
            characters = API.Account("characters")
        except api.APIError:
            return (False, " ".join(traceback.format_exc().splitlines()[-1].split()[1:]))
        hashpassword = hashlib.md5(password).hexdigest()

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
            def alreadyexists(characterName, userID):
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
                else:
                    return (True, '')
                    
            response = alreadyexists(characterName, userID)
            if not response[0]:
                return response
            
            cursor.execute("""
                           INSERT INTO users
                           (id, characterName, characterID, userID, apiKey, password)
                           VALUES ("%s", "%s", "%s", "%s", "%s", "%s")
                           """ % (randomid, characterName, charID, userID, apiKey, hashpassword)
                          )
            
            #add alternate characters also
            for characterName_alt in characters.keys():
                if alreadyexists(characterName_alt, userID)[0]:
                    randomid_alt = "".join([random.choice(string.ascii_letters + string.digits) for x in range(20)])
                    charID_alt = characters[characterName_alt]["characterID"]
                    
                    cursor.execute("""
                                   INSERT INTO users
                                   (id, characterName, characterID, userID, apiKey, password)
                                   VALUES ("%s", "%s", "%s", "%s", "%s", "%s")
                                   """ % (randomid_alt, characterName_alt, charID_alt, userID, apiKey, hashpassword)
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
                user_id = result[0]
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
                if result:
                    return {
                        "characterName" : result[1],
                        "characterID" : result[2],
                        "userID" : result[3],
                        "apiKey" : result[4],
                        "apiObject" : api.API(userid=result[3], apikey=result[4], charid=result[2], characterName=result[1])
                    }
                else:
                    return None
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
    def updateUser(self, characterName, userID, password, new_apiKey, new_password, hostname):
        conn = sqlite3.connect("users/eversible.db")
        cursor = conn.cursor()
        hashpassword = hashlib.md5(password).hexdigest()
        try:
            cursor.execute("""
                           SELECT id, characterName, userID, apiKey
                           FROM users
                           WHERE
                           characterName="%s"
                           """ % characterName
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
                                   WHERE characterName="%s"
                                   """ % altName
                                  )
                except sqlite3.OperationalError:
                    pass
            conn.commit()
            
            response = self.createUser(new_apiKey, userID, characterName, new_password, hostname)
            cursor.close()
            conn.close()
            return response
                
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
    def verifyPassword(self, characterName, password):
        conn = sqlite3.connect("users/eversible.db")
        cursor = conn.cursor()
        hashpassword = hashlib.md5(password).hexdigest()
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
            if cursor.fetchone():
                cursor.close()
                conn.close()
                return True
            else:
                cursor.close()
                conn.close()
                return False
        
    def testIdentity(self, characterName, password, hostname):
        conn = sqlite3.connect("users/eversible.db")
        cursor = conn.cursor()
        hashpassword = hashlib.md5(password).hexdigest()
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
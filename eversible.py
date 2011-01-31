#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import irc.bot
import sqlite3
from core.options import options
from core.config import config

def testDB():
    import evedb
    EVEDB = evedb.DUMP()
    EVEDB.getSystemIDByName("Jita")

try:
    testDB()
except sqlite3.OperationalError:
    print "WARNING: your database is not up to date, many EVErsible functions will not work"
    database = False
else:
    database = True


""" Start the IRC bot """
irc.bot.start(config.get("irc", "host"),
              config.getint("irc", "port"),
              config.get("irc", "nick"),
              config.get("irc", "name"),
              config.get("irc", "channel"),
              config.get("bot", "password"),
              config.get("bot", "prefix"),
              config.getint("bot", "debug_level"),
              database)

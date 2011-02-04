#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import irc.bot
import sqlite3
from core.options import options
from core.config import config
import evedb
import thread
import schedule

database = evedb.testEveDB()
if not database:
    print "WARNING: your static database is not up to date"

sched = schedule.Scheduler()

thread.start_new_thread(sched.start, (5,))

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

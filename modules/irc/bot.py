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

import sys
import socket
import imp
import glob
import traceback
import time
from modules import schedule
import thread

from modules.irc.lib import ircbot
from modules.irc.lib import irclib

from modules.misc import functions
from modules import evedb
from modules import users


USERS = users.DB()
publicCommands = {}
privateCommands = {}

# Scan the "commands" directory and load the modules
def scan():
    publicCommands.clear()
    privateCommands.clear()
    for moduleSource in glob.glob("modules/irc/pub/*.py"):
        name = moduleSource.replace(".py", "").replace("\\","/").split("/")[-1].upper() + "_pub"
        handle = open(moduleSource)
        module = imp.load_module(name, handle, ("pub/" + moduleSource), (".py", "r", imp.PY_SOURCE))
        publicCommands[name] = module
    for moduleSource in glob.glob("modules/irc/priv/*.py"):
        name = moduleSource.replace(".py","").replace("\\","/").split("/")[-1].upper() + "_priv"
        handle = open(moduleSource)
        module = imp.load_module(name, handle, ("priv/" + moduleSource + "_priv"), (".py", "r", imp.PY_SOURCE))
        privateCommands[name] = module

class EVErsibleBot(ircbot.SingleServerIRCBot):
    def __init__(self, config, database):
        self.config = config
        self.HOST = config["irc"]["host"]
        self.PORT = int(config["irc"]["port"])
        self.CHANNEL = config["irc"]["channel"]
        self.NICK = config["irc"]["nick"]
        self.NAME = config["irc"]["name"]
        self.IRCPASS = config["irc"]["password"]
        self.BOTPASS = config["bot"]["password"]
        self.PREFIX = config["bot"]["prefix"]
        self.DEBUG_LEVEL = int(config["bot"]["debug_level"])
        self.VERSION = config["internal"]["version"]
        self.DATABASE = database

        if config["internal"]["verbose"] == "True":
            irclib.DEBUG = True

        ircbot.SingleServerIRCBot.__init__(self, [(self.HOST, self.PORT)], self.NICK, self.NAME)

    def on_ctcp(self, connection, event):
        if event.arguments()[0].upper() == self.BOTPASS.upper():
            scan()
            connection.notice(event.source().split("!")[0], "reloaded modules successfully")
        elif event.arguments()[0].upper() == "VERSION":
            connection.ctcp_reply(event.source().split("!")[0], "VERSION EVErsible v%s" % self.VERSION)
        elif event.arguments()[0].upper() == "TIME":
            connection.ctcp_reply(event.source().split("!")[0], "TIME " + time.asctime())

    def on_welcome(self, connection, event):
        connection.join(self.CHANNEL)
        #start scheduler
        sched = schedule.Scheduler()
        try:
            thread.start_new_thread(sched.start, (), {"connection":connection, "IRCconfig":self.config})
        except:
            connection.privmsg(self.CHANNEL, "There was an error in the scheduler")
            traceback.print_exc()
            thread.start_new_thread(sched.start, (), {"connection":connection, "IRCconfig":self.config})

    def on_privmsg(self, connection, event):
        if event.arguments()[0][0] == self.PREFIX:
            if privateCommands.has_key(event.arguments()[0].split()[0][1:].upper() + "_priv"):
                if self.DATABASE:
                    try:
                        privateCommands[event.arguments()[0].split()[0][1:].upper() + "_priv"].index(connection,event, self.config)
                    except:
                        tb = traceback.format_exc()
                        if self.DEBUG_LEVEL == 0:
                            connection.privmsg(event.source().split("!")[0], "There was an error")
                        elif self.DEBUG_LEVEL == 1:
                            print tb
                            connection.privmsg(event.source().split("!")[0], "There was an error")
                        else:
                            print tb
                            for line in tb.split("\n"):
                               connection.privmsg(event.source().split("!")[0], line)
                else:
                    if not evedb.testEveDB():
                        connection.privmsg(event.source().split("!")[0], "The static CCP dump database is not up to date / not installed correctly")
                    else:
                        connection.privmsg(event.source().split("!")[0], "Reloading database, please try again")

    def on_pubmsg(self, connection, event):
        #check if prefix used
        if event.arguments()[0][0] == self.PREFIX:
            if publicCommands.has_key(event.arguments()[0].split()[0][1:].upper() + "_pub"):
                if self.DATABASE:
                    try:
                        publicCommands[event.arguments()[0].split()[0][1:].upper() + "_pub"].index(connection, event, self.config)
                    except:
                        tb = traceback.format_exc()
                        if self.DEBUG_LEVEL == 0:
                            connection.privmsg(event.target(), "There was an error")
                        elif self.DEBUG_LEVEL == 1:
                            print tb
                            connection.privmsg(event.target(), "There was an error")
                        elif self.DEBUG_LEVEL == 2:
                            print tb
                            connection.privmsg(event.target(), "There was an error")
                            for line in tb.split("\n"):
                                connection.privmsg(event.source().split("!")[0], line)
                        elif self.DEBUG_LEVEL == 3:
                            print tb
                            for line in tb.split("\n"):
                                connection.privmsg(event.target(), line)
                else:
                    if not evedb.testEveDB():
                        connection.privmsg(event.target(), "The static CCP dump database is not up to date / not installed correctly")
                    else:
                        self.DATABASE = True
                        connection.privmsg(event.target(), "Reloading database, please try again") # this is because I'm lazy and totally fake

    def on_part(self, connection, event):
        USERS.removeHostname(event.source())

    def on_nick(self, connection, event):
        USERS.removeHostname(event.source())

    def on_quit(self, connection, event):
        USERS.removeHostname(event.source())
        
    def on_kick(self, connection, event):
        USERS.removeHostnameByNick(event.arguments()[0])


def start(config, database):
    scan()
    bot = EVErsibleBot(config, database)
    bot.start()

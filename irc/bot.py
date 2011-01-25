#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import sys
import socket
import imp
import glob
import traceback
import time

import irc.lib.ircbot as ircbot
import irc.lib.irclib as irclib

import users
USERS = users.DB()

if "-v" in sys.argv:
    irclib.DEBUG = True

VERSION = "0.0.1"

publicCommands = {}
privateCommands = {}

# Scan the "commands" directory and load the modules
def scan():
    publicCommands.clear()
    privateCommands.clear()
    for moduleSource in glob.glob("irc/pub/*.py"):
        name = moduleSource.replace(".py", "").replace("\\","/").split("/")[-1].upper() + "_pub"
        handle = open(moduleSource)
        module = imp.load_module(name, handle, ("pub/" + moduleSource), (".py", "r", imp.PY_SOURCE))
        publicCommands[name] = module
    for moduleSource in glob.glob("irc/priv/*.py"):
        name = moduleSource.replace(".py","").replace("\\","/").split("/")[-1].upper() + "_priv"
        handle = open(moduleSource)
        module = imp.load_module(name, handle, ("priv/" + moduleSource + "_priv"), (".py", "r", imp.PY_SOURCE))
        privateCommands[name] = module
        
    print publicCommands
    print privateCommands

class EVErsibleBot(ircbot.SingleServerIRCBot):
    def __init__(self, host, port, nick, realname, channel, botpass, prefix, debug_level):
        ircbot.SingleServerIRCBot.__init__(self, [(host, port)], nick, realname)
        self.CHANNEL = channel
        self.BOTPASS = botpass
        self.PREFIX = prefix
        self.DEBUG_LEVEL = debug_level

    def on_ctcp(self, connection, event):
        if event.arguments()[0].upper() == self.BOTPASS.upper():
            scan()
            connection.privmsg(event.source().split("!")[0], "reloaded modules successfully")
        elif event.arguments()[0].upper() == "VERSION":
            connection.ctcp_reply(event.source().split("!")[0], "VERSION EVErsible v%s" % VERSION)
        elif event.arguments()[0].upper() == "TIME":
            connection.ctcp_reply(event.source().split("!")[0], "TIME " + time.asctime())

    def on_erroneusnickname(self, connection, event):
        pass

    def on_chanoprivsneeded(self, connection, event):
        connection.privmsg(event.arguments()[0], "ERROR: I need op for that command")

    def on_privnotice(self, connection, event):
        pass

    def on_welcome(self, connection, event):
        connection.join(self.CHANNEL)

    def on_privmsg(self, connection, event):
        if event.arguments()[0][0] == self.PREFIX:
            if privateCommands.has_key(event.arguments()[0].split()[0][1:].upper() + "_priv"):
                try:
                    privateCommands[event.arguments()[0].split()[0][1:].upper() + "_priv"].index(connection,event)
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
                    
    def on_pubmsg(self, connection, event):
        #check if prefix used
        if event.arguments()[0][0] == self.PREFIX:
            if publicCommands.has_key(event.arguments()[0].split()[0][1:].upper() + "_pub"):
                try:
                    publicCommands[event.arguments()[0].split()[0][1:].upper() + "_pub"].index(connection, event)
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

    def on_whoisuser(self, connection, event):
        pass

    def on_kick(self, connection, event):
        USERS.removeHostnameByNick(event.arguments()[0])

    def on_join(self, connection, event):
        #check for banregex
        pass

    def on_namreply(self, connection, event):
        pass

    def on_part(self, connection, event):
        USERS.removeHostname(event.source())
    
    def on_nick(self, connection, event):
        USERS.removeHostname(event.source())

    def on_quit(self, connection, event):
        pass

    def on_mode(self, connection, event):
        pass


def start(host, port, nick, realname, channel, botpass, prefix, debug_level):
    scan()
    bot = EVErsibleBot(host, port, nick, realname, channel, botpass, prefix, debug_level)
    bot.start()

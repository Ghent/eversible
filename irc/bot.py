#!/usr/bin/env python

import sys
import socket
import imp
import glob
import traceback

import irc.lib.ircbot as ircbot
import irc.lib.irclib as irclib


if "-v" in sys.argv:
    irclib.DEBUG = True

VERSION = "0.0.1"

NETWORK = "irc.bytesized-hosting.com"
PORT = 6667
CHANNEL = "#eve"
NICK = "EVErsible"
NAME = "MPrules"
PASSWORD = "pybot"
PREFIX = "."

publicCommands = {}
privateCommands = {}

# Scan the "commands" directory and load the modules
def scan():
    publicCommands.clear()
    privateCommands.clear()
    for moduleSource in glob.glob("irc/pub/*.py"):
        name = moduleSource.replace(".py", "").replace("\\","/").split("/")[-1].upper()
        handle = open(moduleSource)
        module = imp.load_module(name, handle, ("pub/" + moduleSource), (".py", "r", imp.PY_SOURCE))
        publicCommands[name] = module
    for moduleSource in glob.glob("irc/priv/*.py"):
        name = moduleSource.replace(".py","").replace("\\","/").split("/")[-1].upper()
        handle = open(moduleSource)
        module = imp.load_module(name, handle, ("priv/" + moduleSource), (".py", "r", imp.PY_SOURCE))
        privateCommands[name] = module
                
class ModularBot(ircbot.SingleServerIRCBot):
    def on_ctcp(self, connection, event):
        if event.arguments()[0].upper() == PASSWORD.upper():
            scan()
        elif event.arguments()[0].upper() == "VERSION":
            connection.ctcp_reply(event.source().split("!")[0], "VERSION EveBot v%s - copyright mountainpenguin 2011" % VERSION)
        elif event.arguments()[0].upper() == "TIME":
            connection.ctcp_reply(event.source().split("!")[0], "TIME " + time.asctime())

    def on_erroneusnickname(self, connection, event):
        if "is currently being held" in event.arguments()[1]:
            connection.privmsg("NickServ", "RELEASE EveBot pybot")
            connection.nick(NICK)

    def on_chanoprivsneeded(self, connection, event):
        connection.privmsg(event.arguments()[0], "ERROR: I need op for that command")

    def on_privnotice(self, connection, event):
        connection.join(CHANNEL)

    def on_privmsg(self, connection, event):
        print event.arguments()
        
    def on_pubmsg(self, connection, event):
        #check if prefix used
        if event.arguments()[0][0] == PREFIX:
            if publicCommands.has_key(event.arguments()[0].split()[0][1:].upper()):
                try:
                    publicCommands[event.arguments()[0].split()[0][1:].upper()].index(connection, event)
                except:
                    tb = traceback.format_exc()
                    for line in tb.split("\n"):
                        connection.privmsg(event.target(), line)
    
    def on_whoisuser(self, connection, event):
        pass

    def on_kick(self, connection, event):
        #update names when someone is kicked
        kicked = event.arguments()[0].replace("@","").replace("+","").replace("!","").replace("%","").replace("~","").replace("&","")
        #rejoin when kicked
        if kicked == NICK:
            connection.join(event.target())

    def on_join(self, connection, event):
        #check for banregex
        pass
    
    def on_namreply(self, connection, event):
        pass

    def on_part(self, connection, event):
        pass       

    def on_nick(self, connection, event):
        pass

    def on_quit(self, connection, event):
        pass

    def on_mode(self, connection, event):
        pass


def start():
    scan()
    bot = ModularBot([(NETWORK, PORT)], NICK, NAME)
    bot.start()

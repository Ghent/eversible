#!/usr/bin/env python
# vim: filetype=python tabstop=4 expandtab:

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

class EVErsibleBot(ircbot.SingleServerIRCBot):
    def __init__(self, host, port, nick, realname, channel, botpass, prefix):
            ircbot.SingleServerIRCBot.__init__(self, [(host, port)], nick, realname)
            self.channel = channel
            self.botpass = botpass
            self.prefix = prefix

    def on_ctcp(self, connection, event):
        if event.arguments()[0].upper() == self.botpass.upper():
            scan()
        elif event.arguments()[0].upper() == "VERSION":
            connection.ctcp_reply(event.source().split("!")[0], "VERSION EVErsible v%s" % VERSION)
        elif event.arguments()[0].upper() == "TIME":
            connection.ctcp_reply(event.source().split("!")[0], "TIME " + time.asctime())

    def on_erroneusnickname(self, connection, event):
        if "is currently being held" in event.arguments()[1]:
            connection.privmsg("NickServ", "RELEASE EVErsible pybot")
            connection.nick(NICK)

    def on_chanoprivsneeded(self, connection, event):
        connection.privmsg(event.arguments()[0], "ERROR: I need op for that command")

    def on_privnotice(self, connection, event):
        pass

    def on_welcome(self, connection, event):
        connection.join(self.channel)

    def on_privmsg(self, connection, event):
        print event.arguments()

    def on_pubmsg(self, connection, event):
        #check if prefix used
        if event.arguments()[0][0] == self.prefix:
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


def start(host, port, nick, realname, channel, botpass, prefix):
    scan()
    bot = EVErsibleBot(host, port, nick, realname, channel, botpass, prefix)
    bot.start()

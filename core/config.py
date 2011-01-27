#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import ConfigParser


""" Load the configuration """
config = ConfigParser.RawConfigParser()
config.readfp(open(options.configfile))


""" Start the IRC bot """
irc.bot.start(config.get("irc", "host"),
              config.getint("irc", "port"),
              config.get("irc", "nick"),
              config.get("irc", "name"),
              config.get("irc", "channel"),
              config.get("bot", "password"),
              config.get("bot", "prefix"),
              config.getint("bot", "debug_level"))

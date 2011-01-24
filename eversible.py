#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import ConfigParser
from optparse import OptionParser

import irc.bot


""" Get comand line arguments """
parser = OptionParser()
parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                  default=True, help="Run with output")
parser.add_option("-q", "--quiet", action="store_false", dest="verbose",
                  default=False, help="Run with no output")
parser.add_option("-c", "--config", dest="configfile",
                  default="etc/eversible.cfg", help="Config file for IRC "
                  "bot [default: %default]")
(options, args) = parser.parse_args()


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


quit()

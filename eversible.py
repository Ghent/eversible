#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


from optparse import OptionParser
import ConfigParser
import pdb

import irc.bot
<<<<<<< HEAD

from misc import functions


__version__ = "0.0.2"

if __name__ == "__main__":
    # Process comand line arguments
    parser = OptionParser()
    parser.add_option("-v", "--verbose", action="store_true", dest="verbose",
                      default=True, help="Run with output")
    parser.add_option("-q", "--quiet", action="store_false", dest="verbose",
                      default=False, help="Run with no output")
    parser.add_option("-c", "--config", dest="configfile",
                      default="etc/eversible.cfg", help="Config file for IRC "
                      "bot [default: %default]")
    (options, args) = parser.parse_args()

    # Load the configuration
    config = {}
    tmpConf = ConfigParser.SafeConfigParser()
    tmpConf.readfp(open(options.configfile))
    tmpConf.add_section("internal")

    # Pass any relevent options to the dist being passed
    tmpConf.set("internal", "verbose", str(options.verbose))
    tmpConf.set("internal", "version", __version__)

    # Populate the dict containing all settings
    for section in tmpConf.sections():
        config[section] = dict(tmpConf.items(section))

    # Check to see if a valid EVE db exists
    database = functions.testDB()
    if not database:
        print "WARNING: your static database is not up to date"

    # Start the IRC bot
    irc.bot.start(config, database)
=======
import sqlite3
from core.options import options
from core.config import config
import evedb
#import thread
#import schedule

database = evedb.testEveDB()
if not database:
    print "WARNING: your static database is not up to date"

#sched = schedule.Scheduler()

#thread.start_new_thread(sched.start, ())

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
>>>>>>> f3d688a5383726b0be431777b82eb9917d8636ba

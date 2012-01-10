#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


from optparse import OptionParser
import ConfigParser
import pdb
from modules.irc import bot
from modules import evedb

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
    database = evedb.testEveDB()
    if not database:
        print "WARNING: your static database is not up to date"

    # Start the IRC bot
    bot.start(config, database)

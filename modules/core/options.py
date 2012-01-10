#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


from optparse import OptionParser


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

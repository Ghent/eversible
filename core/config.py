#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import ConfigParser


""" Load the configuration """
config = ConfigParser.RawConfigParser()
config.readfp(open(options.configfile))

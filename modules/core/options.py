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

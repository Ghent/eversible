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


from modules import evedb

EVE = evedb.DUMP()

def index(connection, event, config):
    return

    try:
        itemName_user = event.arguments()[0].split()[1]
    except IndexError:
        connection.privmsg(event.target(), "Syntax is: %sbp [item name]" % config["bot"]["prefix"])
    else:
        itemID = EVE.getItemIDByName(itemName_user)
        materials = EVE.getMaterialsByTypeID(itemID)
        itemName = EVE.getItemNameByID(itemID)
        
        tri, pye, mex, iso, noc, zyd, meg, mor = 0,0,0,0,0,0,0,0
        if "Tritanium" in materials.keys():
            tri = materials["Tritanium"]
        if "Pyerite" in materials.keys():
            pye = materials["Pyerite"]
        if "Mexallon" in materials.keys():
            mex = materials["Mexallon"]
        if "Isogen" in materials.keys():
            iso = materials["Isogen"]
        if "Nocxium" in materials.keys():
            noc = materials["Nocxium"]
        if "Zydrine" in materials.keys():
            zyd = materials["Zydrine"]
        if "Megacyte" in materials.keys():
            meg = materials["Megacyte"]
        if "Morphite" in materials.keys():
            mor = materials["Morphite"]
            
        column1_1 = " Tri=%i " % tri
        column1_2 = " Noc=%i " % noc
        
        column2_1 = " Pye=%i " % pye
        column2_2 = " Zyd=%i " % zyd
        
        column3_1 = " Mex=%i " % mex
        column3_2 = " Meg=%i " % meg
        
        column4_1 = " Iso=%i " % iso
        column4_2 = " Mor=%i " % mor
        
        if len(column1_1) > len(column1_2):
            diff = len(column1_1) - len(column1_2)
            column1_2 += " "*diff
        else:
            column1_1 += " "*(len(column1_2) - len(column1_1))
            
        if len(column2_1) > len(column2_2):
            column2_2 += " "*(len(column2_1) - len(column2_2))
        else:
            column2_1 += " "*(len(column2_2) - len(column2_1))
            
        if len(column3_1) > len(column3_2):
            column3_2 += " "*(len(column3_1) - len(column3_2))
        else:
            column3_1 += " "*(len(column3_2) - len(column3_1))
            
        if len(column4_1) > len(column4_2):
            column4_2 += " "*(len(column4_1) - len(column4_2))
        else:
            column4_1 += " "*(len(column4_2) - len(column4_1))
            
        tri,pye,mex,iso,noc,zyd,meg,mor = column1_1, column2_1, column3_1, column4_1, column1_2, column2_2, column3_2, column4_2
            
        connection.privmsg(event.target(), "\x02Item\x02      : %s" % itemName)
        connection.privmsg(event.target(), "\x02Materials\x02 : %s %s %s %s" % (tri, pye, mex, iso))
        connection.privmsg(event.target(), "          : %s %s %s %s" % (noc, zyd, meg, mor))

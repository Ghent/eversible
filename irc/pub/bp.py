#!/usr/bin/python

import db
DUMP = db.DUMP()

def index(connection, event):
    try:
        itemName_user = event.arguments().split()[1]
    except IndexError:
        connection.privmsg(event.target(), "Syntax is: bp [item name]")
    else:
        itemID = DUMP.getItemIDByName(itemName_user)
        materials = DUMP.getMaterialsByTypeID(itemID)
        itemName = DUMP.getItemNameByID(itemID)
        
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
            
        message = """
            \x02Item\x02      : %s
            \x02Materials\x02 : [Tri] %i [Pye] %i [Mex] %i [Iso] %i
                              : [Noc] %i [Zyd] %i [Meg] %i [Mor] %i
        """ % (itemName,
               tri, pye, mex, iso,
               noc, zyd, meg, mor)
        
        for line in message.split("\n"):
            connection.privmsg(event.target(), line.split())
#!/usr/bin/env python

import evedb
import sqlite3

def setIRCColour(input_string, colour, *args):
    """
        colour can be a tuple of (foreground, background)
        or simply a string of foreground
        
        additional optional args can be added:
            "bold", "underlined" and "inverted"
    """
    
    colourdict = {
        "white" : "0",
        "grey" : "1",
        "dark_grey" : "1",
        "blue" : "2",
        "dark_blue" : "2",
        "green" : "3",
        "dark_green" : "3",
        "red" : "4",
        "light_red" : "4",
        "dark_red" : "5",
        "purple" : "6",
        "dark_purple" : "6",
        "yellow" : "7",
        "dark_yellow" : "7",
        "light_yellow" : "8",
        "light_green" : "9",
        "cyan" : "10",
        "dark_cyan" : "10",
        "light_blue" : "12",
        "light_purple" : "13",
        "light_grey" : "14",
        "silver" : "15"  
    }
    
    if type(colour) == tuple:
        fgcolour = colour[0].lower().replace(" ","_")
        bgcolour = colour[1].lower().replace(" ","_")
    else:
        fgcolour = colour.lower().replace(" ","_")
        bgcolour = None
        
    BOLD = "\x02%s\x02"
    UNDERLINED = "\x1f%s\x1f"
    INVERTED = "\x16%s\x16"
    
    for arg in args:
        if arg.lower() == "bold":
            string = BOLD % string
        if arg.lower() == "underlined":
            string = UNDERLINED % string
        if arg.lower() == "inverted":
            string = INVERTED % string
            
    if fgcolour and bgcolour and fgcolour in colourdict.keys() and bgcolor in colourdict.keys():
        #use \x02\x02 "padding" to prevent incorrect colour codes from being sent
        #e.g. \x034145 ISK\x03 outputs '45 ISK' in green
        #     and \x034\x02\x02145 ISK\x03\x02\x02 output '145 ISK' in red
        string = "\x03%s,%s\x02\x02%s\x03\x02\x02" % (colourdict[fgcolour], colourdict[bgcolour], string)
    elif fgcolour and not bgcolour and fgcolour in colourdict.keys():
        string = "\x03%s\x02\x02%s\x03\x02\x02" % (colourdict[fgcolour], string)
    elif bgcolour and not fgcolour and bgcolour in colourdict.keys():
        string = "\x03,%s\x02\x02%s\x03\x02\x02" % (colourdict[bgcolour], string)
    
    return string

    
def security(systemID=None, systemInfo=None):
    EVEDB = evedb.DUMP()
    """
        Returns IRC formatted security for a given systemID
        if systemInfo is inputted then the database call will be omitted
         >= 0.5 in green
         < 0.5 in yellow
         <= 0.0 in red
    """
    if not systemInfo:
        systemInfo = EVEDB.getSystemInfoByID(systemID)
    security = systemInfo["security"]
    if security >= 0.5:
        sec = "\x033\x02\x02%.01f\x03" % security
    elif security < 0.5 and security > 0.0:
        sec = "\x037\x02\x02%.01f\x03" % security
    else:
        sec = "\x035\x02\x02%.02f\x03" % security

    return sec

def findSecurity(systemName):
    EVEDB = evedb.DUMP()
    """
        Returns IRC formatted security for a given systemName
        >= 0.5 in green
        < 0.5 in yellow
        <= 0.0 in red
    """
    sysInfo = EVEDB.getSystemInfoByName(systemName)
    if sysInfo == None:
        return None

    security = sysInfo["security"]
    if security >= 0.5:
        sec = "(\x033\x02\x02%.01f\x03)" % security
    elif security < 0.5 and security > 0.0:
        sec = "(\x037\x02\x02%.01f\x03)" % security
    else:
        sec = "(\x035\x02\x02%.02f\x03)" % security
    return sec

def findName(name, list, count):
    EVEDB = evedb.DUMP()
    match = None
    if match == None:
        match = EVEDB.getSystemName(name)
    if match == None:
        match = EVEDB.getRegionName(name)
    if match != None:
        list[count] = match
        return 1
    return None

def convert_to_human(Time):
    mins, secs = divmod(Time, 60)
    hours, mins = divmod(mins, 60)
    days, hours = divmod(hours, 24)
    weeks, days = divmod(days, 7)
    
    time_str = ""
    if weeks > 0:
        time_str += "%iw " % weeks
    if days > 0:
        time_str += "%id " % days
    if hours > 0:
        time_str += "%ih " % hours
    if mins > 0:
        time_str += "%im " % mins
    if secs > 0:
        time_str += "%is" % secs
    return time_str

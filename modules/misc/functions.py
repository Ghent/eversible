#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


from modules import evedb
import re

def parseIRCBBCode(string):
    """
        Parses artificial "IRC BBCode"
        i.e. [b]test[/b] -> \x02test\x02

        currently very basic,
        e.g. [b]test[b] will return the same as [b]test[/b] or [/b]test[b]

        TO DO:
        make bgcolour and colour no overlap (i.e. closing tag for bgcolour to [/bgcolour]
        us \x03 but retain set [colour])

        Supported tags:
            +--------------+-----------+-------------+
            |  opening     |  closing  | description |
            +--------------+-----------+-------------+
            |    [b]       |   [/b]    | bold        |
            |    [u]       |   [/u]    | underlined  |
            | [colour=x]   | [/colour] | colour      |
            | [bgcolour=x] | [/colour] | background  |
            +--------------+-----------+-------------+

        Supported colours:
            white, grey, dark_grey, blue, dark_blue,
            green, dark_green, red, light_red, dark_red,
            purple, dark_purple, yellow, dark_yellow,
            light_yellow, light_green, cyan, dark_cyan,
            light_blue, light_purple, light_grey, silver

        N.B. dark variants are the same as colours with no
             shade specified
             e.g. red is the same as dark_red
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

    string = string.replace("[b]","\x02").replace("[/b]","\x02")
    string = string.replace("[u]","\x1f").replace("[/u]", "\x1f")
    string = string.replace("[/colour]","\x03\x02\x02")
    #get colours
    colourBBtags = re.finditer("(\[colour=(.*?)\])", string)
    while True:
        try:
            match = colourBBtags.next()
            bbtag = match.group(1)
            colour = match.group(2)
            if colour.lower().replace(" ","_") in colourdict.keys():
                string = string.replace(bbtag, "\x03%s\x02\x02" % colourdict[colour.lower().replace(" ","_")])
        except StopIteration:
            break

    bgcolourBBtags = re.finditer("(\[bgcolour=(.*?)])", string)
    while True:
        try:
            match = bgcolourBBtags.next()
            bbtag = match.group(1)
            colour = match.group(2)
            if colour.lower().replace(" ","_") in colourdict.keys():
                string = string.replace(bbtag, "\x03,%s\x02\x02" % colourdict[colour.lower().replace(" ","_")])
        except StopIteration:
            break

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

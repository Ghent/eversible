#!/usr/bin/env python

import evedb
EVEDB = evedb.DUMP()

def security(systemID=None, systemInfo=None):
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
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

import time
import calendar

from misc import feedparser

from modules import cache


class RSS:
    def __init__(self):
        self.CACHE = cache.CACHE()
        self.RSSFEEDS = {
            "Announcements" : "http://www.eveonline.com/feed/rdfnews.asp?tid=1",
            "Alliances" : "http://www.eveonline.com/feed/rdfnews.asp?tid=7",
            "Devblog" : "http://www.eveonline.com/feed/rdfdevblog.asp",
        }
        self.LASTUPDATE = {
            "Announcements" : self.CACHE.getRSS("Announcements"), # (url, updatetime)
            "Alliances" : self.CACHE.getRSS("Alliances"),
            "Devblog" : self.CACHE.getRSS("Devblog")
        }

    def checkFeed(self, feedName):
        feed = feedparser.parse(self.RSSFEEDS[feedName])
        lastupdate = 0
        lasturl = None
        newitems = []
        for item in feed["items"]:
            date = calendar.timegm(time.strptime(item.date, "%Y-%m-%dT%H:%M+00:00"))
            url = item.link
            try:
                if date > self.LASTUPDATE[feedName][1] and url != self.LASTUPDATE[feedName][0]:
                    if date > lastupdate:
                        lastupdate = date
                        lasturl = url
                    newitems += [item]
            except TypeError:
                newitems += [item]

        item_dict = {}
        for item in newitems:
            item_dict[calendar.timegm(time.strptime(item.date, "%Y-%m-%dT%H:%M+00:00"))] = {
                "date" : calendar.timegm(time.strptime(item.date, "%Y-%m-%dT%H:%M+00:00")),
                "title" : item.title,
                "link" : item.link
            }
        if newitems:
            self.LASTUPDATE[feedName] = (lasturl, lastupdate)
            self.CACHE.insertRSS(feedName, lasturl, lastupdate)

        return item_dict

    def checkFeeds(self):
        feed_dict = {}
        for feedName in self.RSSFEEDS.keys():
            result = self.checkFeed(feedName)
            if result == {}:
                feed_dict[feedName] = None
            else:
                feed_dict[feedName] = result
        return feed_dict

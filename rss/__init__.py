#!/usr/bin/env python
#
# vim: filetype=python tabstop=4 expandtab:


import time
import calendar

import feedparser

import cache


class RSS:
    def __init__(self):
        self.CACHE = cache.CACHE()
        self.RSSFEEDS = {
            "Announcements" : "http://www.eveonline.com/feed/rdfnews.asp?tid=1",
            "Alliances" : "http://www.eveonline.com/feed/rdfnews.asp?tid=7",
            "Devblog" : "http://www.eveonline.com/feed/rdfdevblog.asp",
        }
        self.LASTUPDATE = {
            "Announcements" : self.CACHE.getRSSDate("Announcements"),
            "Alliances" : self.CACHE.getRSSDate("Alliances"),
            "Devblog" : self.CACHE.getRSSDate("Devblog")
        }

    def checkFeed(self, feedName):
        feed = feedparser.parse(self.RSSFEEDS[feedName])
        lastupdate = 0
        newitems = []
        for item in feed["items"]:
            date = calendar.timegm(time.strptime(item.date, "%Y-%m-%dT%H:%M+00:00"))
            if date > self.LASTUPDATE[feedName]:
                if date > lastupdate:
                    lastupdate = date
                newitems += [item]

        item_dict = {}
        for item in newitems:
            item_dict[calendar.timegm(time.strptime(item.date, "%Y-%m-%dT%H:%M+00:00"))] = {
                "date" : calendar.timegm(time.strptime(item.date, "%Y-%m-%dT%H:%M+00:00")),
                "title" : item.title,
                "link" : item.link
            }
        if newitems:
            self.LASTUPDATE[feedName] = lastupdate
            self.CACHE.insertRSSDate(feedName, lastupdate)

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

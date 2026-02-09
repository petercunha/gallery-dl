# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

from gallery_dl.extractor import showcamrips


__tests__ = (
{
    "#url"     : ("https://www.showcamrips.com/show-cam-sex-movies/"
                  "1862964-jade49-chaturbate-webcam-rip-20260209-052637.html"),
    "#category": ("", "showcamrips", "video"),
    "#class"   : showcamrips.ShowcamripsVideoExtractor,
    "#pattern" : r"https://[^/]+/.+\.mp4(?:\?.*)?",

    "id"       : 1862964,
    "slug"     : "jade49-chaturbate-webcam-rip-20260209-052637",
    "model"    : "jade49",
    "model_tag": "Trans",
    "site"     : "Chaturbate",
    "date"     : "dt:2026-02-09 00:00:00",
    "duration" : "00:20:29",
    "iframe_url": str,
    "title"    : str,
    "extension": "mp4",
    "_http_headers": {"Referer": "https://www.showcamrips.com/"},
},

{
    "#url"     : "https://www.showcamrips.com/model/en/urfavevivian/",
    "#category": ("", "showcamrips", "collection"),
    "#class"   : showcamrips.ShowcamripsCollectionExtractor,
    "#pattern" : (r"https://www\.showcamrips\.com/show-cam-sex-movies/"
                  r"\d+-[^/]+\.html"),
    "#count"   : ">= 21",
    "#options" : {"pages": 2},
},

{
    "#url"     : "https://www.showcamrips.com/cat/en/Trans/",
    "#category": ("", "showcamrips", "collection"),
    "#class"   : showcamrips.ShowcamripsCollectionExtractor,
    "#pattern" : (r"https://www\.showcamrips\.com/show-cam-sex-movies/"
                  r"\d+-[^/]+\.html"),
    "#count"   : 20,
    "#options" : {"pages": 1},
},

{
    "#url"     : "https://www.showcamrips.com/site/en/Chaturbate/",
    "#category": ("", "showcamrips", "collection"),
    "#class"   : showcamrips.ShowcamripsCollectionExtractor,
    "#pattern" : (r"https://www\.showcamrips\.com/show-cam-sex-movies/"
                  r"\d+-[^/]+\.html"),
    "#count"   : 20,
    "#options" : {"pages": 1},
},

{
    "#url"     : "https://www.showcamrips.com/best/en/2026-01/",
    "#category": ("", "showcamrips", "collection"),
    "#class"   : showcamrips.ShowcamripsCollectionExtractor,
    "#pattern" : (r"https://www\.showcamrips\.com/show-cam-sex-movies/"
                  r"\d+-[^/]+\.html"),
    "#count"   : 20,
    "#options" : {"pages": 1},
},

{
    "#url"     : "https://www.showcamrips.com/top/en/topweektrans/",
    "#category": ("", "showcamrips", "collection"),
    "#class"   : showcamrips.ShowcamripsCollectionExtractor,
    "#pattern" : (r"https://www\.showcamrips\.com/show-cam-sex-movies/"
                  r"\d+-[^/]+\.html"),
    "#count"   : ">= 20",
    "#options" : {"pages": 1},
},

)

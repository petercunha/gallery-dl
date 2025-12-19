# -*- coding: utf-8 -*-

from gallery_dl.extractor import giphy


__tests__ = (
{
    "#url": "https://giphy.com/search/emiru",
    "#class": giphy.GiphySearchExtractor,
    "#pattern": r"https://media\d+\.giphy\.com/media/v1\..+/giphy\.gif",
    
    "search_tags": "emiru",
},
)

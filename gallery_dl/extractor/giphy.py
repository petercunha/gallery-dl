# -*- coding: utf-8 -*-

# Copyright 2025
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://giphy.com/"""

from .common import Extractor, Message
from .. import text


class GiphyExtractor(Extractor):
    """Base class for giphy extractors"""
    category = "giphy"
    root = "https://giphy.com"
    filename_fmt = "{id}.{extension}"
    archive_fmt = "{id}"


class GiphySearchExtractor(GiphyExtractor):
    """Extractor for Giphy search results"""
    subcategory = "search"
    pattern = r"(?:https?://)?giphy\.com/search/([^/?#]+)"
    directory_fmt = ("{category}", "{search_tags}")
    example = "https://giphy.com/search/QUERY"

    def items(self):
        query = text.unquote(self.groups[0]).replace("-", " ")
        self.kwdict["search_tags"] = query

        url = "https://api.giphy.com/v1/gifs/search"
        params = {
            "rating": "r",
            "offset": "0",
            "limit": "155",
            "type": "gifs",
            "q": query,
            "excludeDynamicResults": "undefined",
            "api_key": "Gc7131jiJuvI7IdN0HZ1D7nh0ow5BU6g",
            "pingback_id": "19b35a5c5cc8856a"
        }

        while True:
            data = self.request_json(url, params=params)
            
            for item in data.get("data", []):
                yield Message.Directory, "", item
                
                # Get the original image url
                images = item.get("images", {})
                if "original" in images and "url" in images["original"]:
                    img_url = images["original"]["url"]
                    item["extension"] = text.ext_from_url(img_url)
                    yield Message.Url, img_url, item

            pagination = data.get("pagination", {})
            total = pagination.get("total_count", 0)
            count = pagination.get("count", 0)
            offset = pagination.get("offset", 0)

            if offset + count >= total:
                break
            
            params["offset"] = str(offset + count)

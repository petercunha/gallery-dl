# -*- coding: utf-8 -*-

# Copyright 2015-2021 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader modules"""

modules = [
    "http",
    "text",
    "ytdl",
    "aria2c",
]


def find(scheme, downloader_type=None):
    """Return downloader class suitable for handling the given scheme"""
    cache_key = scheme if downloader_type is None else scheme + ":" + downloader_type
    try:
        return _cache[cache_key]
    except KeyError:
        pass

    cls = None
    if scheme == "https":
        scheme = "http"

    # Determine which module to load
    module_name = downloader_type or scheme
    if module_name in modules:  # prevent unwanted imports
        try:
            module = __import__(module_name, globals(), None, None, 1)
        except ImportError:
            pass
        else:
            cls = module.__downloader__

    if scheme == "http":
        _cache["http"] = _cache["https"] = cls
        if downloader_type:
            _cache["http:" + downloader_type] = cls
            _cache["https:" + downloader_type] = cls
    else:
        _cache[cache_key] = cls
    return cls


# --------------------------------------------------------------------
# internals

_cache = {}

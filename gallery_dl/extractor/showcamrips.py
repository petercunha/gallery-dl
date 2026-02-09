# -*- coding: utf-8 -*-

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Extractors for https://www.showcamrips.com/"""

from .common import Extractor, Message
from .. import text, util, exception
import itertools

BASE_PATTERN = r"(?:https?://)?(?:www\.)?showcamrips\.com"


class ShowcamripsExtractor(Extractor):
    """Base class for showcamrips extractors"""
    category = "showcamrips"
    root = "https://www.showcamrips.com"
    root_ref = root + "/"


class ShowcamripsVideoExtractor(ShowcamripsExtractor):
    """Extractor for a single video on showcamrips.com"""
    subcategory = "video"
    directory_fmt = ("{category}", "{site}", "{model}")
    filename_fmt = "{id} {slug}.{extension}"
    archive_fmt = "{id}"
    pattern = BASE_PATTERN + r"/show-cam-sex-movies/(\d+)-([^/?#]+)\.html"
    example = ("https://www.showcamrips.com/show-cam-sex-movies/"
               "1862964-jade49-chaturbate-webcam-rip-20260209-052637.html")

    def __init__(self, match):
        ShowcamripsExtractor.__init__(self, match)
        self.video_id, self.slug = match.groups()
        self.headers = {"Referer": self.root_ref}

    def items(self):
        page = self.request(self.url, notfound=self.subcategory).text
        video_url, iframe_url = self._extract_video_url(page)

        data = self.metadata(page)
        data["url"] = video_url
        data["iframe_url"] = iframe_url
        data["_http_headers"] = self.headers
        text.nameext_from_url(video_url, data)

        yield Message.Directory, "", data
        yield Message.Url, video_url, data

    def metadata(self, page):
        info = text.extr(page, '<span class="tl">', "</span>")
        title = text.unescape(text.remove_html(
            text.extr(page, '<div class="h"><h1>', "</h1>")))

        if not title:
            title = text.unescape(text.extr(page, "<title>", ":</title>"))

        return {
            "id"       : text.parse_int(self.video_id),
            "slug"     : self.slug,
            "title"    : title,
            "model"    : text.extr(info, "/model/en/", "/"),
            "model_tag": text.extr(info, "/cat/en/", "/"),
            "site"     : text.extr(info, "/site/en/", "/"),
            "duration" : text.extr(info, "Duration :", "</h3>").strip(),
            "date"     : self.parse_datetime(
                text.extr(info, "Date:", "</h3>").strip(), "%Y.%m.%d"),
        }

    def _extract_video_url(self, page):
        match = text.re(
            r'<iframe[^>]*id="videomoi"[^>]*src="([^"]+)"').search(page)
        if not match:
            raise exception.NotFoundError("video iframe")

        iframe_url = text.urljoin(self.root_ref, text.unescape(match.group(1)))
        iframe_page = self.request(iframe_url, headers=self.headers).text

        if video_url := self._extract_video_source(iframe_page):
            return video_url, iframe_url

        match = text.re(
            r"""window\.location\.href\s*=\s*["']([^"']*play\.php[^"']+)"""
        ).search(iframe_page)
        if not match:
            raise exception.NotFoundError("video")

        play_url = text.urljoin(iframe_url, text.unescape(match.group(1)))
        play_page = self.request(play_url, headers=self.headers).text

        if video_url := self._extract_video_source(play_page):
            return video_url, iframe_url

        raise exception.NotFoundError("video")

    def _extract_video_source(self, page):
        match = text.re(r'<video[^>]*src=["\']([^"\']+)').search(page)
        if not match:
            match = text.re(r'<source[^>]*src=["\']([^"\']+)').search(page)
        if match:
            return text.urljoin(self.root_ref, text.unescape(match.group(1)))
        return None


class ShowcamripsCollectionExtractor(ShowcamripsExtractor):
    """Extractor for video collections on showcamrips.com"""
    subcategory = "collection"
    pattern = (BASE_PATTERN +
               r"/((?:model|cat|site|best|top)/en/[^/?#]+)"
               r"(?:/(\d+)-pg)?/?$")
    example = "https://www.showcamrips.com/model/en/urfavevivian/"

    _find_urls = text.re(
        r'href="(https?://www\.showcamrips\.com/show-cam-sex-movies/'
        r'\d+-[^"#?]+\.html)"'
    ).findall

    def __init__(self, match):
        ShowcamripsExtractor.__init__(self, match)
        self.path, pnum = match.groups()
        self.page_num = text.parse_int(pnum, 1)

    def items(self):
        data = {"_extractor": ShowcamripsVideoExtractor}

        for page in self.pages():
            content = text.extr(page, '<ul class="content">', "</ul>")
            if not content:
                return

            urls = util.unique_sequence(self._find_urls(content))
            if not urls:
                return

            for url in urls:
                yield Message.Queue, url, data

    def pages(self):
        base = f"{self.root}/{self.path}/"
        max_pages = text.parse_int(self.config("pages"), 0)

        for pnum in itertools.count(self.page_num):
            if max_pages and pnum >= self.page_num + max_pages:
                return

            url = base if pnum == 1 else f"{base}{pnum}-pg/"
            response = self.request(url, fatal=False)
            if response.status_code >= 400:
                return

            page = response.text
            yield page

            if f"{base}{pnum + 1}-pg/" not in page:
                return

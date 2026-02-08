# -*- coding: utf-8 -*-

# Copyright 2025 Mike Fährmann
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.

"""Downloader module using aria2c external program"""

import os
import re
import subprocess
from .common import DownloaderBase
from .. import util


class Aria2cDownloader(DownloaderBase):
    scheme = "http"

    def __init__(self, job):
        DownloaderBase.__init__(self, job)
        extractor = job.extractor

        self.exe = self.config("exe", "aria2c")
        self.args = self.config("args")
        self.rate = self.config("rate")
        self.retries = self.config("retries", extractor._retries)
        self.timeout = self.config("timeout", extractor._timeout)
        self.verify = self.config("verify", extractor._verify)
        self.headers = self.config("headers")
        self.cookies = self.config("cookies", True)
        self.mtime = self.config("mtime", True)

    def download(self, url, pathfmt):
        kwdict = pathfmt.kwdict

        # Build aria2c command
        cmd = [self.exe]

        # Add user-specified args first
        if self.args:
            if isinstance(self.args, str):
                cmd.append(self.args)
            else:
                cmd.extend(self.args)

        # Output file
        temppath = pathfmt.temppath
        if self.part:
            pathfmt.part_enable(self.partdir)
            temppath = pathfmt.temppath

        cmd.extend(["-o", temppath])

        # Continue/resume support
        cmd.append("-c")

        # Connection settings
        if self.timeout:
            cmd.extend(["--connect-timeout", str(self.timeout)])
            cmd.extend(["--timeout", str(self.timeout)])

        # Retry settings
        if self.retries is not None:
            if self.retries < 0:
                cmd.append("--max-tries=0")  # infinite retries
            else:
                cmd.extend(["--max-tries", str(self.retries + 1)])

        # Rate limiting
        if self.rate:
            rate_bytes = self._parse_rate(self.rate)
            if rate_bytes:
                cmd.extend(["--max-download-limit", str(rate_bytes)])

        # SSL verification
        if not self.verify:
            cmd.append("--check-certificate=false")

        # Headers
        if self.headers:
            for key, value in self.headers.items():
                cmd.extend(["--header", f"{key}: {value}"])

        # Cookies - forward from session
        if self.cookies:
            cookies = self.session.cookies
            if cookies:
                cookie_str = "; ".join(
                    f"{c.name}={c.value}" for c in cookies
                )
                cmd.extend(["--header", f"Cookie: {cookie_str}"])

        # User agent from session
        if self.session.headers.get("User-Agent"):
            cmd.extend(["--user-agent", self.session.headers["User-Agent"]])

        # URL to download
        cmd.append(url)

        # Execute aria2c
        self.out.start(pathfmt.path)
        self.log.debug("Command: %s", " ".join(cmd))

        try:
            process = util.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            returncode = process.wait()
        except FileNotFoundError:
            self.log.error("aria2c executable not found: %s", self.exe)
            return False
        except Exception as exc:
            self.log.error("Failed to execute aria2c: %s", exc)
            return False

        if returncode != 0:
            self.log.error("aria2c returned with exit code %d", returncode)
            # Clean up failed download file if not using part files
            if not self.part:
                util.remove_file(temppath)
            return False

        # Set modification time if requested
        if self.mtime:
            if "_http_lastmodified" in kwdict:
                mtime = kwdict["_http_lastmodified"]
            else:
                # Try to get from response headers if available
                mtime = None
            if mtime:
                try:
                    import time
                    timestamp = time.mktime(mtime.timetuple())
                    os.utime(temppath, (timestamp, timestamp))
                except Exception:
                    pass

        return True

    def _parse_rate(self, rate):
        """Parse rate limit string to bytes per second"""
        if isinstance(rate, (int, float)):
            return int(rate)

        rate = str(rate).lower().strip()
        multipliers = {
            "k": 1024,
            "kb": 1024,
            "m": 1024 ** 2,
            "mb": 1024 ** 2,
            "g": 1024 ** 3,
            "gb": 1024 ** 3,
        }

        for suffix, multiplier in multipliers.items():
            if rate.endswith(suffix):
                try:
                    return int(float(rate[:-len(suffix)]) * multiplier)
                except ValueError:
                    return None

        try:
            return int(float(rate))
        except ValueError:
            return None


__downloader__ = Aria2cDownloader

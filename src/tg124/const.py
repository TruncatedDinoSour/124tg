#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""constants"""

from typing import Final

PROXY_API: Final[
    str
] = "https://gimmeproxy.com/api/getProxy?post=true&get=true&user-agent=true&supportsHttps=true&protocol=http&minSpeed=20&curl=true"
PROXY_TEST: Final[str] = "https://example.com/"
PROXY_TIMEOUT: Final[float] = 10

DEFAULT_TRANSLATE_SOURCE: Final[str] = "EN"

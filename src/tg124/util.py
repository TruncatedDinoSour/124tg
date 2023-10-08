#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""utilities"""

import asyncio

import aiohttp

from . import const


async def get_proxies() -> dict[str, str]:
    async with aiohttp.ClientSession() as session:
        while True:
            async with session.get(const.PROXY_API) as resp:
                proxy: str = await resp.text()

            try:
                async with session.get(
                    const.PROXY_TEST,
                    timeout=const.PROXY_TIMEOUT,
                    proxy=proxy,
                ) as resp:
                    if not resp.ok:
                        raise Exception("proxy failed")
            except Exception:
                await asyncio.sleep(1)
                continue

            return {"proxy": proxy}

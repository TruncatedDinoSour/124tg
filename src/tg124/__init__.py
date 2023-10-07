#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""124tg bot"""

import asyncio
import logging

import telegram as tg
import telegram.ext as tg_ext

from .cmds import cmds


class Bot124tg:
    def __init__(self, token: str) -> None:
        self.app = tg_ext.Application.builder().token(token).build()

    def enable_logging(self) -> None:
        logging.basicConfig(
            format="%(name)s @ %(asctime)s - [%(levelname)s] %(message)s",
            level=logging.INFO,
        )

        logging.getLogger("httpx").setLevel(logging.WARNING)

    def run(self) -> None:
        asyncio.get_event_loop().run_until_complete(cmds.init_app(self.app))  # type: ignore
        self.app.run_polling(allowed_updates=tg.Update.ALL_TYPES)

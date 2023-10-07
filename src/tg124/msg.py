#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""telegram message"""

import textwrap

import telegram as tg
import telegram.ext as tg_ext


class Message:
    __slots__: tuple[str, str] = "upt", "ctx"

    def __init__(
        self,
        upt: tg.Update,
        ctx: tg_ext.ContextTypes.DEFAULT_TYPE,
    ) -> None:
        if upt.message is None or ctx.args is None:
            raise ValueError("invalid message ( missing update message or arguments )")

        self.upt: tg.Update = upt
        self.ctx: tg_ext.ContextTypes.DEFAULT_TYPE = ctx

    async def reply(self, text: str, markdown: bool = False) -> None:
        for page in textwrap.wrap(text, 1900, replace_whitespace=False):
            await (self.upt.message.reply_markdown_v2 if markdown else self.upt.message.reply_text)(page)  # type: ignore

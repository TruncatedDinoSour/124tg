#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""telegram message"""

import typing
from functools import lru_cache

import telegram as tg
import telegram.ext as tg_ext


class Message:
    __slots__: tuple[str, str] = "upt", "ctx"

    def __init__(
        self,
        upt: tg.Update,
        ctx: tg_ext.ContextTypes.DEFAULT_TYPE,
        *,
        _check: bool = True,
    ) -> None:
        if _check and None in (upt.message, ctx.args, upt.effective_user):
            raise ValueError("invalid message ( missing update message or arguments )")

        self.upt: tg.Update = upt
        self.ctx: tg_ext.ContextTypes.DEFAULT_TYPE = ctx

    @classmethod
    @lru_cache(1)
    def empty(cls) -> "Message":
        return cls(None, None, _check=False)  # type: ignore

    @property
    def msg(self) -> tg.Message:
        return self.upt.message  # type: ignore

    @property
    def text(self) -> str:
        return self.msg.text or ""  # type: ignore

    @property
    def text_no_cmd(self) -> str:
        return (self.text.split(maxsplit=1) + [""])[1]

    @property
    def user(self) -> tg.User:
        return self.upt.effective_user  # type: ignore

    async def reply(
        self,
        *args: typing.Any,
        typ: str = "text",
        **kwargs: typing.Any,
    ) -> None:
        await getattr(self.upt.message, f"reply_{typ}")(*args, **kwargs)

    async def reply_md(
        self,
        *args: typing.Any,
        **kwargs: typing.Any,
    ) -> None:
        await self.upt.message.reply_markdown(*args, **kwargs)  # type: ignore

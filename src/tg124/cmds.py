#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""default commands"""

from .cmdmgr import Cmdmgr
from .conv import Boolean
from .msg import Message

cmds: Cmdmgr = Cmdmgr()


@cmds.new
async def ping(msg: Message) -> None:
    """ping the bot"""

    await msg.reply_md(f"{msg.user.mention_markdown()} pong")


@cmds.new
async def happy(msg: Message, is_happy: Boolean) -> None:
    """am i happy"""

    await msg.reply_md(":)" if is_happy else ":(")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""default commands"""

from .cmdmgr import Cmdmgr
from .msg import Message

cmds: Cmdmgr = Cmdmgr()


@cmds.new
async def ping(msg: Message) -> None:
    """ping the bot"""

    await msg.reply_md(f"{msg.user.mention_markdown()} pong")

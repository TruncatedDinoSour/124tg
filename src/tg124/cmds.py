#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""default commands"""

from . import ai as ai_impl
from . import cmdmgr, conv
from . import msg as m

cmds: cmdmgr.Cmdmgr = cmdmgr.Cmdmgr()


@cmds.new
async def ping(msg: m.Message) -> None:
    """ping the bot"""

    await msg.reply_md(f"{msg.user.mention_markdown()} pong")


@cmds.new
async def happy(msg: m.Message, is_happy: conv.Boolean) -> None:
    """am i happy"""

    await msg.reply_md(":)" if is_happy else ":(")


@cmds.new
async def ai(
    msg: m.Message,
    text: str,
    model: ai_impl.TextAI = ai_impl.TextAI.gpt4,
    regen: conv.Boolean = conv.Boolean.true(),
) -> None:
    """generate ai text responses"""

    await msg.reply_md(
        (await ai_impl.gen_ai_text(text, model, await regen.convert()))[:1900]
        or "*no ai respose*"
    )

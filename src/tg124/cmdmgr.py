#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""command manager"""

import time
import typing
from functools import wraps

import telegram as tg
import telegram.ext as tg_ext

from .conv import Convertor
from .msg import Message


async def get_admins(chat: tg.Chat | None, ttl: float = 900) -> set[int]:
    """cached get_administrators api"""

    if chat is None:
        raise ValueError("no chat given")

    if getattr(get_admins, "__cache__", None) is None:
        get_admins.__cache__: dict[int, tuple[set[int], float]] = {}  # type: ignore

    admins, last = get_admins.__cache__.get(chat.id, (None, 0))  # type: ignore

    if admins is not None and time.time() - last < ttl:
        return admins

    admins = set(m.user.id for m in await chat.get_administrators())
    last = time.time()

    get_admins.__cache__[chat.id] = admins, last  # type: ignore

    return admins


class Cmdmgr:
    def __init__(self) -> None:
        self.app: typing.Any = None
        self.cmds: dict[
            str, typing.Callable[..., typing.Coroutine[typing.Any, typing.Any, None]]
        ] = {}

        @self.new
        async def start(msg: Message) -> None:
            """print help page / usage"""

            await msg.reply(
                "\n".join(
                    f"/{cname} -- {cfn.__doc__ or 'no help provided'}"
                    for cname, cfn in self.cmds.items()
                    if cname != "start"
                )
            )

        self.cmds["help"] = start

    def new(
        self,
        fn: typing.Callable[..., typing.Coroutine[typing.Any, typing.Any, None]],
    ) -> typing.Callable[..., typing.Coroutine[typing.Any, typing.Any, None]]:
        if fn.__name__ in self.cmds:
            raise ValueError("command already assigned")

        if not fn.__annotations__:
            raise ValueError("command is not annotated")

        @wraps(fn)
        async def wrapper(
            upt: tg.Update,
            ctx: tg_ext.ContextTypes.DEFAULT_TYPE,
        ) -> None:
            msg: Message = Message(upt=upt, ctx=ctx)

            args: dict[str, typing.Any] = {}

            for line in filter(bool, msg.text_no_cmd.split(";")):  # type: ignore
                arg, val = line.split(":", 1)
                typ: typing.Type[typing.Any] = fn.__annotations__.get(arg, str)

                args[arg] = (
                    typ(val, msg).convert() if issubclass(typ, Convertor) else typ(val)
                )

            try:
                await fn(msg, **args)  # type: ignore
            except Exception as e:
                await msg.reply(f"error !! `{e.__class__.__name__} -- {e}`", "markdown_v2")
                raise e

        self.cmds[fn.__name__] = wrapper
        return wrapper

    def admin(
        self,
        fn: typing.Callable[..., typing.Coroutine[typing.Any, typing.Any, None]],
    ) -> typing.Callable[..., typing.Coroutine[typing.Any, typing.Any, None]]:
        @self.new
        @wraps(fn)
        async def wrapper(msg: Message) -> None:
            if msg.upt.effective_user is None:
                raise ValueError("no effective user is executing this command")

            if msg.upt.effective_user.id in await get_admins(msg.upt.effective_chat):
                await fn(msg)
                return

            await msg.reply("u have no rights to execute this command")

        return wrapper

    def init_app(self, app: typing.Any) -> None:
        for cname, cfn in self.cmds.items():
            app.add_handler(tg_ext.CommandHandler(cname, cfn))

        self.app = app

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""command manager"""

import typing
from functools import wraps

import telegram as tg
import telegram.ext as tg_ext

from .conv import Convertor
from .msg import Message


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
        self, fn: typing.Callable[..., typing.Coroutine[typing.Any, typing.Any, None]]
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

            for line in (upt.message.text.split(maxsplit=1) + [""])[1].splitlines():  # type: ignore
                arg, val = line.split(":", 1)
                typ: typing.Type[typing.Any] = fn.__annotations__.get(arg, str)

                args[arg] = (
                    typ(val, msg).convert() if issubclass(typ, Convertor) else typ(val)
                )

            try:
                await fn(msg, **args)  # type: ignore
            except Exception as e:
                await msg.reply(f"error !! `{e.__class__.__name__} -- {e}`")
                raise e

        self.cmds[fn.__name__] = wrapper
        return wrapper  # type: ignore

    def init_app(self, app: typing.Any) -> None:
        for cname, cfn in self.cmds.items():
            app.add_handler(tg_ext.CommandHandler(cname, cfn))

        self.app = app

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""command manager"""

import asyncio
import time
import typing
from enum import Enum
from functools import wraps, lru_cache

import telegram as tg
import telegram.constants as tg_const
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

        @lru_cache(1)
        def _gen_help() -> str:
            help_page: str = (
                "command syntax : /command arg:value;arg1:value 1;arg2:value 2\n\n"
            )

            for cname, cfn in self.cmds.items():
                if cname == "start":
                    continue

                help_page += f"/{cname}"

                varnames: typing.Dict[str, typing.Type[typing.Any]] = cfn._fn.__annotations__.copy()  # type: ignore

                del varnames["msg"]
                del varnames["return"]

                if varnames:
                    help_page += " " + ", ".join(
                        f"`{var}`(`{typ.__name__}`)" for var, typ in varnames.items()
                    )

                help_page += f" -- {cfn.__doc__ or '*no help provided*'}\n"

            return help_page.strip()

        @self.new
        async def start(msg: Message) -> None:
            """print help page / usage"""
            await msg.reply_md(_gen_help())

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

            if upt.effective_chat:
                await upt.effective_chat.send_action(tg_const.ChatAction.TYPING)

            args: dict[str, typing.Any] = {}

            try:
                for line in filter(bool, msg.text_no_cmd.split(";")):  # type: ignore
                    arg, val = (line.split(":", maxsplit=1) + [""])[:2]
                    typ: typing.Type[typing.Any] = fn.__annotations__.get(arg, str)

                    if issubclass(typ, Convertor):
                        args[arg] = await typ(val, msg).convert()
                    elif issubclass(typ, Enum):
                        try:
                            args[arg] = typ[val]
                        except KeyError:
                            pass
                    else:
                        args[arg] = typ(val)

                asyncio.get_event_loop().create_task(fn(msg, **args))
            except Exception as e:
                await msg.reply_md(f"error !! `{e.__class__.__name__} -- {e}`")
                raise e

        wrapper._fn = fn  # type: ignore
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

    async def init_app(self, app: typing.Any) -> None:
        await app.bot.delete_my_commands()  # type: ignore
        await app.bot.set_my_commands(  # type: ignore
            tuple(
                (cname, cfn.__doc__ or "no help provided")
                for cname, cfn in self.cmds.items()
            )
        )

        for cname, cfn in self.cmds.items():
            app.add_handler(tg_ext.CommandHandler(cname, cfn))

        self.app = app

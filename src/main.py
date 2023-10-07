#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""124tg"""

import logging
import os
from typing import Any
from warnings import filterwarnings as filter_warnings

import telegram as tg
import telegram.ext as tg_ext

from tg124 import cmdmgr, conv

c = cmdmgr.Cmdmgr()


@c.new
async def no(msg: cmdmgr.Message) -> None:
    """no"""

    await msg.reply("kys `please`")


def main() -> int:
    """entry/main function"""

    logging.basicConfig(
        format="%(name)s @ %(asctime)s - [%(levelname)s] %(message)s",
        level=logging.INFO,
    )

    logging.getLogger("httpx").setLevel(logging.WARNING)

    app: Any = (
        tg_ext.Application.builder().token(os.environ.get("TG_TOKEN") or "").build()
    )
    # app.add_handler(tg_ext.CommandHandler("start", start))
    c.init_app(app)

    app.run_polling(allowed_updates=tg.Update.ALL_TYPES)

    return 0


if __name__ == "__main__":
    assert main.__annotations__.get("return") is int, "main() should return an integer"

    filter_warnings("error", category=Warning)
    raise SystemExit(main())

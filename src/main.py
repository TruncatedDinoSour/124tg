#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""124tg"""

import os
from warnings import filterwarnings as filter_warnings

from tg124 import Bot124tg


def main() -> int:
    """entry/main function"""

    b: Bot124tg = Bot124tg(os.environ.get("TG_TOKEN") or "")
    b.enable_logging()
    b.run()

    return 0


if __name__ == "__main__":
    assert main.__annotations__.get("return") is int, "main() should return an integer"

    filter_warnings("error", category=Warning)
    raise SystemExit(main())

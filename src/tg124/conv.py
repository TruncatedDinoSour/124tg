#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""convertors"""

import typing
from abc import ABC, abstractmethod

from .msg import Message


class Convertor(ABC):
    """base convertor class for custom types in commands"""

    def __init__(self, what: str, msg: Message) -> None:
        self.what: str = what
        self.msg: Message = msg

    @abstractmethod
    async def convert(self) -> typing.Any:
        ...


class Boolean(Convertor):
    """helps to convert boolean string literals to bools"""

    async def convert(self) -> bool:
        return bool(self)

    def __bool__(self) -> bool:
        return self.what.lower() in ("1", "true", "yes", "y", "ok")

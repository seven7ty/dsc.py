# -*- coding: utf-8 -*-

from typing import Union


def str_bool(val: str) -> bool:
    return True if str(val).lower() == "true" else False


def null(val: str) -> Union[str, None]:
    return None if str(val).lower() == 'null' else val


def int_or_none(val: Union[str, None]) -> Union[int, None]:
    return int(val) if val is not None else val

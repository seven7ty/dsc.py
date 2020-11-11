from typing import Union


def str_bool(str_bool: str) -> bool:
    return True if str(str_bool).lower() == "true" else False


def null(val: str) -> Union[str, None]:
    return None if str(val).lower() == 'null' else val

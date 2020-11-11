from typing import Any
from ..utils import null, str_bool


class User:
    def __init__(self, data: dict):
        self.links: int = int(data.get("links", 0))
        self.premium: bool = str_bool(data.get("premium"))
        self.blacklisted: bool = str_bool(data.get("blacklisted"))
        self.staff: Any = null(data.get("staff"))
        self.raw: dict = data

    def __int__(self) -> int:
        return self.links

    def __bool__(self) -> bool:
        return self.premium

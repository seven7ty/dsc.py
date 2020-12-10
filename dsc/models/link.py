# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2020 Paul Przybyszewski

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from typing import Union
from .embed import Embed
from ..utils import str_bool, int_or_none


class Link:
    def __init__(self, data: dict):
        if "s_name" not in data:
            self.embed: Union[Embed, None] = Embed(dict(data.get("embed"))) if "embed" in dict(data) else None
        else:
            self.agents: Union[str, None] = data.get("agents", None)
            self.click_other: Union[int, None] = data.get("click_other", None)
            self.embed: Embed = Embed(
                {"title": data.get("s_name", None), "desc": data.get("desc", None), "color": data.get('color', None),
                 "saying": data.get("saying", None), "image": data.get('image', None)})
        self.name: Union[str, None] = data.get("link", None)
        self.url: Union[str, None] = f"https://dsc.gg/{self.name}" if self.name is not None else None
        self.type: Union[str, None] = data.get("type", None)
        self.suspended: bool = str_bool(data.get("suspended"))
        self.unique: int = int(data.get("unique", 0))
        self.recent: tuple = (data.get("recent", None), int_or_none(data.get("recent_time", None)))
        self.redirect: Union[str, None] = data.get("redirect", None)
        self.owner_id: Union[int, None] = int_or_none(data.get("owner", None))
        self.clicks: int = int(data.get("clicks", 0))
        self.raw: dict = data

    def __int__(self) -> int:
        return self.clicks

    def __str__(self) -> str:
        return self.name

    def __bool__(self) -> bool:
        return self.suspended

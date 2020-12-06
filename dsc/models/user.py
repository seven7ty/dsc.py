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

from typing import Any
from ..utils import null, str_bool


class User:
    def __init__(self, data: dict):
        self.links: int = int(data.get("links", 0))
        self.premium: bool = str_bool(data.get("premium", "false"))
        self.blacklisted: bool = str_bool(data.get("blacklisted", "false"))
        self.staff: Any = null(data.get("staff", "null"))
        self.raw: dict = data

    def __int__(self) -> int:
        return self.links

    def __bool__(self) -> bool:
        return self.premium

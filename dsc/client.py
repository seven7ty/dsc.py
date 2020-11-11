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

from aiohttp import ClientSession
from .models.link import Link
from .models.user import User
from .exceptions import NoToken, BadToken, Forbidden
from typing import Union, List
from asyncio import sleep


class Client:
    def __init__(self, token: str = None):
        self._token: str = token
        self._ses: ClientSession = ClientSession()
        self._transfer_cache: list = []

    async def _cache_transfer(self, link: Union[str, int]) -> None:
        self._transfer_cache.append(link)
        await sleep(60)
        self._transfer_cache.remove(link)

    async def get_link(self, link: Union[str, int]) -> Union[Link, None]:
        res = await self._ses.get(f"https://dsc.gg/api/link/{link}")
        if res.status == 200:
            return Link(dict(await res.json()))
        return None

    async def get_links(self, user_id: Union[int, str]) -> Union[List[Link], None]:
        res = await self._ses.get(f"https://dsc.gg/api/links/{user_id}")
        if res.status == 200:
            return [Link(dict(link)) for link in list(await res.json())]
        return None

    async def get_user(self, user_id: Union[int, str]) -> Union[User, None]:
        res = await self._ses.get(f"https://dsc.gg/api/info/{user_id}")
        if res.status == 200:
            return User(dict(await res.json()))
        return None

    async def get_announcements(self, user_id: Union[int, str]) -> list:
        res = await self._ses.get(f"https://dsc.gg/api/announcements/{user_id}")
        return list(await res.json())

    async def create_link(self, link: Union[str, int], redirect: str, link_type: str) -> None:
        if self._token is None:
            raise NoToken("You need to pass in a Discord OAuth2 Token into the object constructor to use this function")

        res = await self._ses.post("https://dsc.gg/api/create",
                                   headers={"contentType": "application/json"},
                                   json={"link": link, "redirect": redirect, "type": link_type, "token": self._token})
        if res.status != 200:
            if res.status == 401:
                raise BadToken("Invalid OAuth2 token provided")
            elif res.status == 403:
                raise Forbidden("You cannot perform this action. (create_link)")

    async def update_link(self, link: Union[str, int], redirect: str, link_type: str) -> None:
        if self._token is None:
            raise NoToken("You need to pass in a Discord OAuth2 Token into the object constructor to use this function")

        res = await self._ses.post("https://dsc.gg/api/update",
                                   headers={"contentType": "application/json"},
                                   json={"link": link, "redirect": redirect, "type": link_type, "token": self._token})

        if res.status != 200:
            if res.status == 401:
                raise BadToken("Invalid OAuth2 token provided")
            elif res.status == 403:
                raise Forbidden("You cannot perform this action. (update_link)")

    async def delete_link(self, link: Union[str, int]) -> None:
        if self._token is None:
            raise NoToken("You need to pass in a Discord OAuth2 Token into the object constructor to use this function")

        res = await self._ses.post("https://dsc.gg/api/delete",
                                   headers={"contentType": "application/json"},
                                   json={"link": link, "token": self._token})

        if res.status != 200:
            if res.status == 401:
                raise BadToken("Invalid OAuth2 token provided")
            elif res.status == 403:
                raise Forbidden("You cannot perform this action. (delete_link)")

    async def transfer_link(self, link: Union[str, int], user_id: Union[str, int], comments: str = "None") -> None:
        if link in self._transfer_cache:
            return
        if self._token is None:
            raise NoToken("You need to pass in a Discord OAuth2 Token into the object constructor to use this function")

        res = await self._ses.post("https://dsc.gg/api/transfer",
                                   json={"link": link, "comments": comments, "transfer": str(user_id),
                                         "token": self._token})

        if res.status != 200:
            if res.status == 401:
                raise BadToken("Invalid OAuth2 token provided")
            elif res.status == 403:
                raise Forbidden("You cannot perform this action. (transfer_link)")
        await self._cache_transfer(link=link)

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

from aiohttp import ClientSession, ClientTimeout
from .models.link import Link
from .models.user import User
from .models.announcement import Announcement
from .exceptions import (
    NoToken, Unauthorized,
    Forbidden, BearerNoToken,
    BadLinkType, InternalServerError,
    BadRequest, ServiceUnavailable
)
from typing import (Union, List,
                    NoReturn, Any)
from asyncio import (sleep, AbstractEventLoop,
                     get_event_loop)

correlation: dict = {
    400: BadRequest,
    401: Unauthorized,
    403: Forbidden,
    500: InternalServerError,
    503: ServiceUnavailable,
    BadRequest: "Something went wrong",
    Unauthorized: "The Discord OAuth Token you provided was invalid",
    Forbidden: "You cannot perform this action",
    InternalServerError: "The API returned a 500 status code",
    ServiceUnavailable: "The dsc.gg API is currently unavailable"
}


def has_token(func):
    def _decorator(self, *args, **kwargs):
        if self._token is None:
            raise NoToken(
                "You need to pass in a Discord OAuth2 Token into the object constructor to use this function")
        return func(self, *args, **kwargs)

    return _decorator


def validate(link_type: str) -> bool:
    valid: list = ["server", "bot", "template"]
    return link_type.lower() in valid


def validate_link_type(func):
    def _decorator(self, *args, **kwargs):
        if len(args) > 0:
            if validate(args[2]):
                return func(self, *args, **kwargs)
        else:
            link = kwargs.get("link_type", None)
            if link is not None and validate(link):
                return func(self, *args, **kwargs)
        raise BadLinkType(
            "link_type must be either 'bot', 'server' or 'template'")

    return _decorator


def transfer_ratelimit(func):
    def _decorator(self, *args, **kwargs):
        if self.transfer_is_ratelimited:
            self._v(f"Cannot transfer link - ratelimited.")
            return
        return func(self, *args, **kwargs)

    return _decorator


class Client:
    def __init__(self, token: str = None, bearer: bool = False, verbose: bool = False,
                 connection_timeout: Union[int, float, None] = 15):
        if token is not None:
            self._token: str = token.strip()
        else:
            self._token = None

        self._bearer: bool = bearer

        if self._bearer and self._token is None:
            raise BearerNoToken(
                "If bearer is True, a token must be passed into the constructor")

        if self._bearer and self._token[:7] != "Bearer ":
            self._token: str = "Bearer " + self._token

        self.connection_timeout: Union[int, float, None] = connection_timeout
        self._loop: AbstractEventLoop = get_event_loop()
        self._ses: ClientSession = ClientSession(
            loop=self._loop,
            timeout=ClientTimeout(
                total=self.connection_timeout if self.connection_timeout >= 0 or self.connection_timeout is None else 15))
        self.transfer_is_ratelimited: bool = False
        self._verbose: bool = verbose

    @staticmethod
    def _raise_from_status(code: int) -> Any:
        return correlation.get(code, None)

    @staticmethod
    def _format(link: str) -> str:
        if link.startswith("https://dsc.gg/"):
            return link[15:]
        elif link.startswith('dsc.gg/'):
            return link[7:]
        return link

    async def _rate_limit_transfer(self) -> None:
        self.transfer_is_ratelimited = True
        await sleep(300)
        self.transfer_is_ratelimited = False

    async def get_link(self, link: Union[str, int]) -> Union[Link, None]:
        res = await self._ses.get(f"https://dsc.gg/api/link/{self._format(link)}")

        if res.status == 200:
            data = dict(await res.json())
            data["link"] = link
            return Link(data=data)

        self._v(f"Couldn't fetch link '{link}'")
        return None

    async def get_links(self, user_id: Union[int, str]) -> Union[List[Link], List]:
        res = await self._ses.get(f"https://dsc.gg/api/links/{user_id}")

        if res.status == 200:
            return [Link(data=dict(link)) for link in list(await res.json())]

        self._v(
            f"Couldn't fetch links for user ID '{user_id}', returning an empty list")
        return []

    async def top_links(self) -> Union[List[Link], List]:
        res = await self._ses.get("https://dsc.gg/api/top-links")

        if res.status == 200:
            return [Link(data=dict(link)) for link in list(await res.json())]

        self._v("Couldn't fetch top links, returning an empty list")
        return []

    async def fetch_links(self, page: int) -> Union[List[Link], List]:
        res = await self._ses.get(f"https://dsc.gg/api/all-links?page={page if page > 0 else 1}")

        if res.status == 200 and (_ := await res.text()).lower() != "none":
            return [Link(data=dict(link)) for link in list(await res.json())]

        self._v("Couldn't fetch links, returning an empty list")
        return []

    async def get_user(self, user_id: Union[int, str]) -> Union[User, None]:
        res = await self._ses.get(f"https://dsc.gg/api/info/{user_id}")

        if res.status == 200:
            return User(data=dict(await res.json()))

        self._v(f"Couldn't fetch user with the ID '{user_id}'")
        return None

    async def get_announcements(self, user_id: Union[int, str]) -> Union[List[Announcement], List]:
        res = await self._ses.get(f"https://dsc.gg/api/announcements/{user_id}")

        if res.status == 200:
            return list([Announcement(data=dict(a)) for a in list(await res.json())])

        self._v(f"Couldn't fetch announcements for user ID '{user_id}'")
        return []

    @has_token
    @validate_link_type
    async def create_link(self, link: Union[str, int], redirect: str, link_type: str) -> NoReturn:
        res = await self._ses.post("https://dsc.gg/api/create",
                                   headers={"contentType": "application/json"},
                                   json={"link": self._format(link), "redirect": redirect, "type": link_type.lower(),
                                         "token": self._token})
        if res.status != 200:
            if (err := self._raise_from_status(res.status)) is not None:
                raise err(correlation.get(err))

        self._v(f"Link '{link}' created.")

    @has_token
    @validate_link_type
    async def update_link(self, link: Union[str, int], redirect: str, link_type: str) -> NoReturn:
        res = await self._ses.post("https://dsc.gg/api/update",
                                   headers={"contentType": "application/json"},
                                   json={"link": self._format(link), "redirect": redirect, "type": link_type.lower(),
                                         "token": self._token})

        if res.status != 200:
            if (err := self._raise_from_status(res.status)) is not None:
                raise err(correlation.get(err))

        self._v(f"Link '{link}' updated.")

    @has_token
    async def delete_link(self, link: Union[str, int]) -> NoReturn:
        res = await self._ses.post("https://dsc.gg/api/delete",
                                   headers={"contentType": "application/json"},
                                   json={"link": self._format(link), "token": self._token})

        if res.status != 200:
            if (err := self._raise_from_status(res.status)) is not None:
                raise err(correlation.get(err))

        self._v(f"Link '{link}' deleted.")

    @has_token
    @transfer_ratelimit
    async def transfer_link(self, link: Union[str, int], user_id: Union[str, int], comments: str = "None") -> NoReturn:
        res = await self._ses.post("https://dsc.gg/api/transfer",
                                   json={"link": self._format(link), "comments": comments, "transfer": str(user_id),
                                         "token": self._token}, headers={"contentType": "application/json"})

        if res.status != 200:
            if (err := self._raise_from_status(res.status)) is not None:
                raise err(correlation.get(err))
        else:
            self._v(
                f"Successful transfer to user ID '{user_id}' - 5 minute ratelimit")
            self._loop.create_task(self._rate_limit_transfer())

    def _v(self, msg: str) -> NoReturn:
        if self._verbose:
            print(msg)

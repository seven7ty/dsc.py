# -*- coding: utf-8 -*-

"""
MIT License

Copyright (c) 2020 wulf

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

from typing import Union, Optional, List, Any
from aiohttp import ClientSession
from asyncio import AbstractEventLoop, get_event_loop
from .models import *
from .utils import raise_for_status, format_link, match_link_type
from .exceptions import NotFound

BASE: str = 'https://api.dsc.gg/v2'


class Client:
    """
    The main class used to interact with the dsc.gg API.

    Attributes
    ----------
    token: :class:`str`
        The dsc.gg API Token to authenticate with
    loop: :class:`asyncio.AbstractEventLoop`
        The optional asyncio event loop to use
    timeout: Union[:class:`int`, :class:`float`, :class:`NoneType`]
        The total connection timeout for requests in seconds, 0 or None means no timeout, defaults to 30
    """

    def __init__(self, token: str, loop: AbstractEventLoop = get_event_loop(), timeout: Union[int, float, None] = 30):
        self.loop: AbstractEventLoop = loop if isinstance(loop, AbstractEventLoop) else get_event_loop()
        self._ses: ClientSession = ClientSession(timeout=timeout,
                                                 headers={"Authorization": f"<{token}>"},
                                                 loop=self.loop)

    @staticmethod
    def insert_embed_fields(body: dict, embed: Embed) -> dict:
        """
        Inserts attributes of the :class:`dsc.Embed` object into the passed dictionary.

        Parameters
        ----------
        body: :class:`dict`
            The dict to update with new values
        embed: :class:`dsc.Embed`
            The embed object

        Returns
        -------
        :class:`dict`
            The updated body dictionary
        """

        attrs: dict = {
            'title': 'meta_title',
            'description': 'meta_description',
            'color': 'meta_color',
            'image': 'meta_image'
        }

        for k, v in attrs.items():
            if (a := getattr(embed, k, None)) is not None:
                body[v]: Any = a

        return body

    async def get_user(self, user_id: int) -> Union[User, None]:
        """|coro|

        Get a dsc.gg user.

        Parameters
        ----------
        user_id: :class:`int`
            The Discord ID of the user you want to fetch

        Returns
        -------
        Union[:class:`dsc.User`, None]
            The user object just fetched, or None if not found

        Raises
        ------
        dsc.Unauthorized
            The token passed was invalid
        dsc.Forbidden
            Attempted to access premium features or the token is invalid
        dsc.BadRequest
            The arguments passed are malformed
        dsc.RequestEntityTooLarge
            The passed link slug or password is too long
        """

        res = await self._ses.get(url=BASE + f"/user/{user_id}")

        if res.status == 200:
            return User(data=dict(await res.json()))
        try:
            raise_for_status(status=res.status)
        except NotFound:
            return None

    async def get_link(self, link: str) -> Union[Link, None]:
        """|coro|

        Get a dsc.gg link.

        Parameters
        ----------
        link: :class:`str`
            The link to search for, can be the slug or the whole link.

        Returns
        -------
        Union[:class:`dsc.Link`, None]
            The link object just fetched, or None if not found

        Raises
        ------
        dsc.Unauthorized
            The token passed was invalid
        dsc.Forbidden
            Attempted to access premium features or the token is invalid
        dsc.BadRequest
            The arguments passed are malformed
        dsc.RequestEntityTooLarge
            The passed link slug or password is too long
        """

        res = await self._ses.get(url=BASE + f"/link/{format_link(link=link)}")

        if res.status == 200:
            return Link(data=dict(await res.json()))

        try:
            raise_for_status(status=res.status)
        except NotFound:
            return None

    async def search(self, query: str, limit: Optional[int] = None) -> Union[List[Link], list]:
        if limit is None:
            res = await self._ses.get(url=BASE + f"/search/{query}")
        else:
            res = await self._ses.get(url=BASE + f"/search/{query}", json={"limit": int(limit)})

        try:
            raise_for_status(status=res.status)
            return list([Link(data=link) for link in list(await res.json())])
        except NotFound:
            return []

    async def create_link(self, link: str, redirect: str, embed: Optional[Embed] = None, password: Optional[str] = None,
                          unlisted: bool = False) -> None:
        """|coro|

        Create a dsc.gg link.

        Parameters
        ----------
        link: :class:`str`
            The slug or full link that should be created
        redirect: :class:`str`
            The redirect that should be bound to this link
        embed: Optional[:class:`dsc.Embed`]
            The embed to use for the link
        password: Optional[:class:`str`]
            The password restricting access to the link
        unlisted: :class:`bool`
            If the link shouldn't be listed; defaults to False

        Raises
        ------
        dsc.Unauthorized
            The token passed was invalid
        dsc.Forbidden
            Attempted to access premium features or the token is invalid
        dsc.BadRequest
            The arguments passed are malformed
        dsc.RequestEntityTooLarge
            The passed link slug or password is too long
        """

        link: str = format_link(link=link)
        matched_type: tuple = match_link_type(link=link)
        body: dict = {"link": link, "type": matched_type[1], "redirect": redirect}

        if embed is not None:
            if not isinstance(embed, Embed):
                raise TypeError(f"Embed must be type 'dsc.Embed, got '{embed.__class__.__name__}'")

            body: dict = self.insert_embed_fields(body=body, embed=embed)

        if password is not None:
            body['password']: str = password
        if unlisted is True:
            body['unlisted']: bool = True

        res = await self._ses.post(url=BASE + f'/link/{link}', json=body)
        raise_for_status(status=res.status)

    async def update_link(self, link: str, redirect: Optional[str] = None, embed: Optional[Embed] = None,
                          password: Optional[str] = None,
                          unlisted: bool = False) -> None:
        """|coro|

        Update a dsc.gg link.

        Parameters
        ----------
        link: :class:`str`
            The slug or full link leading to the one being updated
        redirect: Optional[:class:`str`]
            The redirect that should be bound to this link
        embed: Optional[:class:`dsc.Embed`]
            The embed to use for the link
        password: Optional[:class:`str`]
            The password restricting access to the link
        unlisted: Optional[:class:`bool`]
            If the link shouldn't be listed - defaults to False

        Raises
        ------
        dsc.Unauthorized
            The token passed was invalid
        dsc.Forbidden
            Attempted to access premium features or the token is invalid
        dsc.BadRequest
            The arguments passed are malformed
        dsc.RequestEntityTooLarge
            The passed link slug or password is too long
        dsc.NotFound
           The passed link slug doesn't exist
        """

        link: str = format_link(link=link)
        body: dict = {"link": link}

        if embed is not None:
            if not isinstance(embed, Embed):
                raise TypeError(f"Embed must be type 'dsc.Embed, got '{embed.__class__.__name__}'")

            body: dict = self.insert_embed_fields(body=body, embed=embed)

        if password is not None:
            body['password']: str = password
        if unlisted is True:
            body['unlisted']: bool = True
        if redirect is not None:
            body['redirect']: str = redirect

        res = await self._ses.patch(url=BASE + f'/link/{link}', json=body)
        raise_for_status(status=res.status)

    async def delete_link(self, link: str) -> None:
        """|coro|

        Delete a dsc.gg link.

        Parameters
        ----------
        link: :class:`str`
            The slug or full link leading to the one being deleted

        Raises
        ------
        dsc.Unauthorized
            The token passed was invalid
        dsc.Forbidden
            Attempted to access premium features or the token is invalid
        dsc.BadRequest
            The arguments passed are malformed
        dsc.RequestEntityTooLarge
            The passed link slug or password is too long
        dsc.NotFound
           The passed link slug doesn't exist
        """

        res = await self._ses.delete(url=BASE + f'/link/{link}')
        raise_for_status(status=res.status)

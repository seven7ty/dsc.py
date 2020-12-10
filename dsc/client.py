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

from typing import Union, Optional, List, Any, NoReturn
from aiohttp import ClientSession
from asyncio import AbstractEventLoop, get_event_loop
from .models import Embed, Link, User
from .utils import format_link, match_link_type
from .exceptions import *

__all__ = (
    'Client'
)

BASE: str = 'https://api.dsc.gg/v2'


class Client:
    """
    The main class used to interact with the dsc.gg API.

    Attributes
    ----------
    key: :class:`str`
        The dsc.gg API Token to authenticate with
    loop: :class:`asyncio.AbstractEventLoop`
        The optional asyncio event loop to use
    timeout: Optional[Union[:class:`int`, :class:`float`]]
        The total connection timeout for requests in seconds, 0 or None means no timeout; defaults to 30
    raise_for_status: :class:`bool`
        Whether or not to raise an exception when a non-positive status is returned; defaults to False.
        Keep in mind that 429 (Rate Limited) errors are raised no matter what.
    verbose: :class:`bool`
        Whether or not to log things that happen under the hood to the console; defaults to False
    """

    def __init__(self, key: str, loop: AbstractEventLoop = get_event_loop(),
                 timeout: Optional[Union[int, float]] = 30, verbose: bool = False, raise_for_status: bool = False):
        self.loop: AbstractEventLoop = loop if isinstance(loop, AbstractEventLoop) else get_event_loop()
        self._ses: ClientSession = ClientSession(timeout=timeout,
                                                 headers={"Authorization": f"{key}"},
                                                 loop=self.loop)
        self.verbose: bool = verbose
        self.__raise_for_status: bool = raise_for_status

    def _raise_for_status(self, status: int) -> NoReturn:
        """
        Raise an adequate error from the passed status code.

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

        if self.__raise_for_status:
            correlation: dict = {
                401: Unauthorized,
                400: BadRequest,
                413: RequestEntityTooLarge,
                403: Forbidden,
                404: NotFound,
                Unauthorized: "The token passed is invalid",
                Forbidden: "Attempted to access premium features or the token is invalid",
                BadRequest: "The arguments passed are malformed",
                RequestEntityTooLarge: "The passed link slug or password is too long",
                NotFound: "The link doesn't exist"
            }
            if (e := correlation.get(status, None)) is not None:
                raise e(correlation.get(e))
        elif status == 403:
            raise Forbidden('Invalid API token passed into the constructor')

    @staticmethod
    def _insert_embed_fields(body: dict, embed: Embed) -> dict:
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

    async def get_user(self, user_id: int) -> Optional[User]:
        """|coro|

        Get a dsc.gg user.

        Parameters
        ----------
        user_id: :class:`int`
            The Discord ID of the user you want to fetch

        Returns
        -------
        Optional[:class:`dsc.User`]
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

        self.__v(msg='Fetching user with ID %s...' % str(user_id))
        res = await self._ses.get(url=BASE + f"/user/{user_id}")

        if res.status == 200:
            self.__v(msg='User with the ID %s was found.' % str(user_id))
            return User(data=dict(await res.json()))
        elif res.status == 429:
            raise RateLimitedError('get_user has hit the rate limit, whitelist your application')
        try:
            self._raise_for_status(status=res.status)
        except NotFound:
            return None

    async def get_link(self, link: str) -> Optional[Link]:
        """|coro|

        Get a dsc.gg link.

        Parameters
        ----------
        link: :class:`str`
            The link to search for, can be the slug or the whole link.

        Returns
        -------
        Optional[:class:`dsc.Link`]
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

        self.__v(msg='Fetching link \'%s\'...' % link)
        res = await self._ses.get(url=BASE + f"/link/{format_link(link=link)}")

        if res.status == 200:
            self.__v(msg='Link \'%s\' found.' % link)
            return Link(data=dict(await res.json()))
        elif res.status == 429:
            raise RateLimitedError('get_link has hit the rate limit, whitelist your application')
        try:
            self._raise_for_status(status=res.status)
        except NotFound:
            return None

    async def search(self, query: str, limit: Optional[int] = None) -> List[Link]:
        """
        Search the dsc.gg link database.

        Parameters
        ----------
        query: :class:`str`
            The query to execute on the API
        limit: Optional[:class:`int`]
            The number of the links to return, returns all if not specified.

        Returns
        -------
        List[:class:`dsc.Link`]
            A list containing the fetched results.
        """

        if not limit:
            res = await self._ses.get(url=BASE + f"/search/{query}")
        else:
            res = await self._ses.get(url=BASE + f"/search/{query}?limit={limit}")
        if res.status == 429:
            raise RateLimitedError('search has hit the rate limit, whitelist your application')
        try:
            self._raise_for_status(status=res.status)
            return list([Link(data=link) for link in list(await res.json())])
        except NotFound:
            return []

    async def create_link(self, link: str, redirect: str, embed: Optional[Embed] = None, password: Optional[str] = None,
                          unlisted: bool = False) -> int:
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
        dsc.RateLimitedError
            A long rate limit was exhausted.
        """

        link: str = format_link(link=link)
        matched_type: tuple = match_link_type(link=link)
        body: dict = {"link": link, "type": matched_type[1], "redirect": redirect}

        if embed is not None:
            if not isinstance(embed, Embed):
                raise TypeError(f"Embed must be type 'dsc.Embed, got '{embed.__class__.__name__}'")

            body: dict = self._insert_embed_fields(body=body, embed=embed)

        if password is not None:
            body['password']: str = password
        if unlisted is True:
            body['unlisted']: bool = True

        self.__v(msg='Attempting to create link \'%s\'...' % link)
        res = await self._ses.post(url=BASE + f'/link/{link}', json=body)
        if res.status == 429:
            raise RateLimitedError('create_link has hit the rate limit, whitelist your application')
        self._raise_for_status(status=res.status)
        self.__v(msg='Link \'%s\' created.' % link)
        return res.status

    async def update_link(self, link: str, redirect: Optional[str] = None, embed: Optional[Embed] = None,
                          password: Optional[str] = None,
                          unlisted: bool = False) -> int:
        """|coro|

        Update a dsc.gg link.

        Parameters
        ----------
        link: :class:`str`
            The slug or full link leading of the one being updated
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
        dsc.RateLimitedError
            A long rate limit was exhausted.
        """

        link: str = format_link(link=link)
        body: dict = {"link": link}

        if embed is not None:
            if not isinstance(embed, Embed):
                raise TypeError(f"Embed must be type 'dsc.Embed, got '{embed.__class__.__name__}'")

            body: dict = self._insert_embed_fields(body=body, embed=embed)

        if password is not None:
            body['password']: str = password
        if unlisted is True:
            body['unlisted']: bool = True
        if redirect is not None:
            body['redirect']: str = redirect

        self.__v(msg='Attempting to update link \'%s\'...' % link)
        res = await self._ses.patch(url=BASE + f'/link/{link}', json=body)
        if res.status == 429:
            raise RateLimitedError('update_link has hit the rate limit, whitelist your application')
        self._raise_for_status(status=res.status)
        self.__v(msg='Link \'%s\' updated.' % link)
        return res.status

    async def delete_link(self, link: str) -> int:
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
        dsc.RateLimitedError
            A long rate limit was exhausted.
        """

        self.__v(msg='Attempting to delete link \'%s\'...' % link)
        res = await self._ses.delete(url=BASE + f'/link/{link}')
        if res.status == 429:
            raise RateLimitedError('delete_link has hit the rate limit, whitelist your application')
        self._raise_for_status(status=res.status)
        self.__v(msg='Link \'%s\' deleted.' % link)
        return res.status

    def __v(self, msg: str) -> None:
        """
        Log info in the console if `verbose` is True.

        Parameters
        ----------
        msg: :class:`str`
            The message to log in the console
        """

        if self.verbose:
            print(msg)

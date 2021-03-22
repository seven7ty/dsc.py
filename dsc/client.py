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

from typing import Optional, List, NoReturn, Union
from aiohttp import ClientSession, ClientTimeout
from asyncio import AbstractEventLoop, get_event_loop
from .models import Embed, Link, User, Color, App
from .enums import *

__all__ = (
    'Client'
)

BASE: str = 'https://api.dsc.gg/v2'


class DSCGGError(RuntimeError):
    pass


class Client:
    """
    The main class used to interact with the dsc.gg API.

    Attributes
    ----------
    key: :class:`str`
        The dsc.gg API Token to authenticate with
    loop: :class:`asyncio.AbstractEventLoop`
        The optional asyncio event loop to use
    timeout: Optional[:class:`aiohttp.ClientTimeout`]
        The total connection timeout from this object will be used as the total timeout for the client; defaults to 30
    verbose: :class:`bool`
        Whether or not to log things that happen under the hood to the console; defaults to False
    """

    def __init__(self, key: str, loop: AbstractEventLoop = get_event_loop(),
                 timeout: Optional[ClientTimeout] = ClientTimeout(total=30), verbose: bool = False):
        if not isinstance(timeout, ClientTimeout):
            timeout = ClientTimeout(total=30)
        self.loop: AbstractEventLoop = loop if isinstance(loop, AbstractEventLoop) else get_event_loop()
        self._ses: ClientSession = ClientSession(timeout=timeout,
                                                 headers={"Authorization": key},
                                                 loop=self.loop)
        self.verbose: bool = verbose

    @staticmethod
    def format_link(link: str) -> str:
        """
        Formats the 'dsc.gg/whatever' links to be only the slug

        Parameters
        ----------
        link: :class:`str`
            The link to format

        Returns
        -------
        :class:`str`
            The slug of the passed link
        """

        if link.startswith("https://dsc.gg/"):
            return link[15:]
        elif link.startswith("http://dsc.gg/"):
            return link[14:]
        elif link.startswith('dsc.gg/'):
            return link[7:]
        return link

    @staticmethod
    def match_link_type(link: str) -> str:
        """
        Returns the tuple corresponding to the link passed.

        Returns
        -------
        :class:`tuple`
            The tuple with the first item being the invoking pattern, and second being the actual link type
        """

        cor = {
            LinkType.Server: 'server',
            LinkType.Bot: 'bot',
            LinkType.Template: 'template'
        }
        if not link.startswith('https://'):
            link = 'https://' + link
        link_f = link[:int(link.rindex('/') + 1)]
        try:
            link_type = LinkType(link_f)
            return cor[link_type]
        except (KeyError, ValueError):
            return 'link'

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

        for key, value in embed.__dict__.items():
            if isinstance(value, Color):
                body['meta'][key] = str(value)
                continue
            body['meta'][key] = value

        return body

    @staticmethod
    async def _raise_for_status(response: dict) -> NoReturn:
        """
        Raise an adequate error from the passed status code.

        Parameters
        ----------
        response: :class:`dict`
            The response json.
        """

        code = str(response['code']).lower()
        enum = getattr(ResponseCodes, code)

        if not str(enum.value.code).startswith('2'):
            raise DSCGGError(f'{enum.value.code} ({code}): {enum.value.meaning}')

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

        self.__v(message='Fetching user with ID %s...' % str(user_id))
        res = await self._ses.get(url=BASE + f"/user/{user_id}")
        res_ = await res.json()

        if res.status == 200 and bool(res_['success']):
            self.__v(message='User with the ID %s was found.' % str(user_id))
            return User(data=dict(res_)['payload'])
        if res.status != 404:
            await self._raise_for_status(response=res_)
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

        self.__v(message='Fetching link \'%s\'...' % link)
        res = await self._ses.get(url=BASE + f"/link/{self.format_link(link=link)}")

        if res.status == 200:
            self.__v(message='Link \'%s\' found.' % link)
            return Link(data=dict(await res.json())['payload'])
        if res.status != 404:
            await self._raise_for_status(response=await res.json())
        return None

    async def get_user_links(self, user_id: int) -> List[Link]:
        """
        Returns all of the user's links.

        Parameters
        ----------
        user_id: :class:`int`
            The Discord user ID of the user to return links for.

        Returns
        -------
        List[:class:`dsc.Link`]
            A list of the links belonging to the user.
        """

        self.__v('Attempting to fetch links for user with ID \'%s\'...' % str(user_id))
        res = await self._ses.get(url=BASE + f'/user/{user_id}/links')

        if res.status == 200:
            self.__v('Returning links found...')
            return list([Link(link) for link in dict(await res.json())['payload']])
        if res.status != 404:
            await self._raise_for_status(response=await res.json())
        return []

    async def get_user_apps(self, user_id: int) -> List[App]:
        """
        Returns all of the user's apps.

        Parameters
        ----------
        user_id: :class:`int`
            The Discord user ID of the user to return apps for.

        Returns
        -------
        List[:class:`dsc.Link`]
            A list of apps belonging to the user.
        """

        self.__v('Attempting to fetch apps for a user with ID \'%s\'...' % str(user_id))
        res = await self._ses.get(url=BASE + f'/user/{user_id}/links')

        if res.status == 200:
            self.__v('Returning apps found...')
            return list([App(app) for app in dict(await res.json())['payload']])
        if res.status != 404:
            await self._raise_for_status(response=await res.json())
        return []

    async def get_app(self, app_id: Union[int, str]) -> Optional[App]:
        """
        Get a dsc.gg developer app.

        Parameters
        ----------
        app_id: Union[:class:`str`, :class:`int`]
            The id of the app to get.

        Returns
        -------
        Optional[:class:`dsc.App`]
        """

        self.__v(message='Fetching app with id \'%s\'...' % str(app_id))
        res = await self._ses.get(url=BASE + f"/app/{app_id}")

        if res.status == 200:
            self.__v(message='App with id \'%s\' found.' % str(app_id))
            return App(data=dict(await res.json())['payload'])
        if res.status != 404:
            await self._raise_for_status(response=await res.json())
        return None

    async def get_top_links(self) -> List[Link]:
        """
        Get top links from dsc.gg.

        Returns
        -------
        List[:class:`dsc.Link`]
            The top links requested.
        """

        self.__v(message='Fetching top links...')
        res = await self._ses.get(url=BASE + '/top')

        if res.status == 200:
            self.__v(message='Successfully fetched top links.')
            return list([Link(link) for link in dict(await res.json())['payload']])
        if res.status != 404:
            await self._raise_for_status(response=await res.json())
        return []

    async def search(self, query: str, limit: Optional[int] = None, link_type: Optional[str] = None) -> List[Link]:
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

        Raises
        ------
        dsc.DSCGGError
            Something went wrong.
        """

        self.__v(message='Compiling search URL...')
        url = BASE + f"/search?q={query}"
        if limit:
            url += f'&limit={limit}'
        if link_type.lower() in ['server', 'bot', 'template']:
            url += f'&type={link_type.lower()}'
        self.__v(message='Fetching search results...')
        res = await self._ses.get(url=url)
        if res.status == 404:
            return []
        await self._raise_for_status(response=await res.json())
        self.__v(message='Links found.')
        return list([Link(data=link) for link in list(dict(await res.json())['payload'])])
    
    async def get_butt(self) -> str:
        """
        Returns a butt from dsc.gg's secret endpoint

        Parameters
        ----------
        N/A

        Returns
        -------
        :class:`str`
            Butt.

        Raises
        ------
        dsc.DSCGGError
            Something went wrong.
        """
        
        self.__v(message='Fetching butt')
        res = await self._ses.get(url=BASE + "/butt")

        if res.status == 200:
            self.__v(message='Butt found.')
            return str(await res.text())
        if res.status != 404:
            await self._raise_for_status(response=await res.json())
        return None

    async def create_link(self, link: str, redirect: str, embed: Optional[Embed] = None,
                          password: Optional[str] = None,
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
        dsc.DSCGGError:
            Something went wrong.
        """

        link: str = self.format_link(link=link)
        if redirect.startswith('https://'):
            redirect = redirect.replace('https://', '')
        body: dict = {"type": self.match_link_type(redirect), "redirect": redirect}

        if embed is not None:
            if not isinstance(embed, Embed):
                raise TypeError(f"Embed must be type 'dsc.Embed, got '{embed.__class__.__name__}'")

            body: dict = self._insert_embed_fields(body=body, embed=embed)

        if password is not None:
            body['password']: str = password
        if unlisted is True:
            body['unlisted']: bool = True

        self.__v(message='Attempting to create link \'%s\'...' % link)
        res = await self._ses.post(url=BASE + f'/link/{link}', json=body)
        await self._raise_for_status(response=await res.json())
        if res.status == 201:
            self.__v(message='Link \'%s\' created.' % link)
        else:
            self.__v(message='failed to create link \'%s\'' % link)
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
        dsc.DSCGGError:
            Something went wrong.
        """

        link: str = self.format_link(link=link)
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

        self.__v(message='Attempting to update link \'%s\'...' % link)
        res = await self._ses.patch(url=BASE + f'/link/{link}', json=body)
        await self._raise_for_status(response=await res.json())
        self.__v(message='Link \'%s\' updated.' % link)
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
        dsc.DSCGGError:
            Something went wrong.
        """

        link: str = self.format_link(link=link)
        self.__v(message='Attempting to delete link \'%s\'...' % link)
        res = await self._ses.delete(url=BASE + f'/link/{link}')
        await self._raise_for_status(response=await res.json())
        self.__v(message='Link \'%s\' deleted.' % link)
        return res.status

    def __v(self, message: str) -> None:
        """
        Log info in the console if `verbose` is True.

        Parameters
        ----------
        message: :class:`str`
            The message to log in the console
        """

        if self.verbose:
            print(message)

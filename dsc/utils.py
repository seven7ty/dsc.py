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

from .exceptions import *
from enum import Enum
from typing import NoReturn


class LinkType(Enum):
    """Used to correlate a link with its dsc.gg type"""

    Server = ('https://discord.gg/', 'server')
    Template = ('https://discord.com/template/', 'template')
    Bot = ('https://discord.com/oauth2/', 'bot')


def match_link_type(link: str) -> tuple:
    """
    Returns the tuple corresponding to the link passed.

    Returns
    -------
    :class:`tuple`
        The tuple with the first item being the invoking pattern, and second being the actual link type
    """

    if not link.startswith('https://'):
        link = 'https://' + link
    link_f = link[:link.rindex('/') + 1]
    try:
        return LinkType(link_f)
    except ValueError:
        return link, 'link'


def raise_for_status(status: int) -> NoReturn:
    """
    Raise the adequate error from the passed status code.

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
    elif link.startswith('dsc.gg/'):
        return link[7:]
    return link

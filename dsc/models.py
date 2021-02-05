from __future__ import annotations

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

from datetime import datetime
from typing import Union, Any
from colorsys import hsv_to_rgb

__all__ = (
    'App',
    'User',
    'Link',
    'Embed',
    'Colour', 'Color'
)


class App:
    """
    Represents a dsc.gg developer application.

    .. container:: operations

        .. describe:: x == y

             Checks if two users are equal.

        .. describe:: x != y

             Checks if two users are not equal.

        .. describe:: bool(x)

            Returns whether or not the app is verified (whitelisted).

    Attributes
    ----------
    id: :class:`int`
        The Discord ID of the user
    owner_id: :class:`int`
        The Discord user ID of the app's owner
    created_at: :class:`datetime.datetime`
        The time at which the app was created
    verified: :class:`bool`
        Whether the app is verified or not
    key: Optional[:class:`str`]
        The key for the app, present only if you're the owner
    """

    __slots__ = ('id', 'owner_id', 'created_at', 'verified', 'key')

    def __init__(self, data: dict):
        self.id: int = data.get('id', None)
        self.owner_id: int = data.get('owner_id', None)
        self.created_at: datetime = datetime.utcfromtimestamp(int(data['created_at']) / 1000)  # Fix the timestamp
        self.verified: bool = data.get('verified', False)
        self.key: str = data.get('key', None)

    def to_dict(self) -> dict:
        """
        Get the :class:`dsc.User` in the form of a :class:`dict`

        Returns
        -------
        :class:`dict`
            The dictionary product of the conversion
        """

        result: dict = {
            key: getattr(self, key)
            for key in self.__slots__
            if key[0] != '_' and hasattr(self, key)
        }

        return result

    def __repr__(self) -> str:
        return '<App id=%s>' % str(self.id)

    def __eq__(self, other) -> bool:
        return self.__repr__() == repr(other)

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __bool__(self) -> bool:
        return self.verified


class User:
    """
    Represents a dsc.gg user.

    .. container:: operations

        .. describe:: x == y

             Checks if two users are equal.

        .. describe:: x != y

             Checks if two users are not equal.

        .. describe:: int(x)

             Returns the ID of the user.

        .. describe:: bool(x)

            Returns whether or not the user has premium or not.

    Attributes
    ----------
    id: :class:`int`
        The Discord ID of the user
    premium: :class:`bool`
        Whether or not the user has premium
    verified: :class:`bool`
        Whether or not the user is verified
    blacklisted: :class:`bool`
        Whether or not the user is blacklisted
    joined_at: :class:`datetime.datetime`
        The time at which the account was created
    """

    __slots__ = ('id', 'premium', 'verified', 'joined_at', 'blacklisted')

    def __init__(self, data: dict):
        self.id: int = int(data.get('id'))
        self.premium: bool = data.get('premium', False)
        self.verified: bool = data.get('verified', False)
        self.joined_at: datetime = datetime.utcfromtimestamp(int(data.get('joined_at')) / 1000)
        self.blacklisted: bool = data.get('blacklisted', False)

    def to_dict(self) -> dict:
        """
        Get the :class:`dsc.User` in the form of a :class:`dict`

        Returns
        -------
        :class:`dict`
            The dictionary product of the conversion
        """

        result: dict = {
            key: getattr(self, key)
            for key in self.__slots__
            if key[0] != '_' and hasattr(self, key)
        }

        return result

    def __int__(self) -> int:
        return self.id

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, User) and self.__repr__() == repr(other)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __bool__(self) -> bool:
        return self.premium

    def __repr__(self) -> str:
        return '<User id=%s>' % str(self.id)


class Link:
    """
    Represents a dsc.gg link.

    .. container:: operations

        .. describe:: x == y

             Checks if two links are equal.

        .. describe:: x != y

             Checks if two links are not equal.

        .. describe:: str(x)

             Returns the slug of the link.

        .. describe:: int(x)

            Returns the ID of the link's owner.

        .. describe:: bool(x)

            Returns whether or not the link is unlisted.

    Attributes
    ----------
    id :class:`str`
        The link id (slug), ex. if the link is 'dsc.gg/statch' it'll be 'statch'
    domain :class:`str`
        The domain of the link
    owner_id :class:`int`
        The Discord ID of the link's owner
    editors :class:`list`
        A list of Discord IDs of users that can edit the link
    redirect :class:`str`
        The final link the dsc.gg one leads to
    created_at :class:`datetime.datetime`
        The time the link was created
    created_at :class:`datetime.datetime`
        The last time the link was bumped
    unlisted :class:`bool`
        If the link is hidden from top pages and discovery
    blacklisted :class:`bool`
        :class:`bool` signifying if the link is blacklisted
    type :class:`str`
        The type of the link, can be either 'server' or 'bot'
    embed :class:`dsc.Embed`
        The embed of the link
    """

    __slots__ = (
        'id', 'redirect', 'created_at', 'bumped_at', 'unlisted', 'disabled', 'type', 'embed',
        'domain', 'owner_id')

    def __init__(self, data: dict):
        bump = data.get('bumped_at', None)
        self.id: str = data.get('id', None)
        self.owner_id: int = data.get('owner', None)
        self.redirect: str = data.get('redirect', None)
        self.created_at: datetime = datetime.utcfromtimestamp(int(data.get('created_at')) / 1000)
        self.bumped_at: datetime = datetime.utcfromtimestamp(int(bump) / 1000) if bump else None
        self.unlisted: bool = data.get('unlisted', False)
        self.disabled: bool = data.get('disabled', False)
        self.embed: Embed = Embed.from_dict(dict(data)['meta'])
        self.type: str = data.get('type', None)
        self.domain: str = data.get('domain', None)

    def to_dict(self) -> dict:
        """
        Get the :class:`dsc.Link` in the form of a :class:`dict`

        Returns
        -------
        :class:`dict`
            The :class:`dict` product of the conversion
        """

        result: dict = {
            key: getattr(self, key)
            for key in self.__slots__
            if key[0] != '_' and hasattr(self, key)
        }

        return result

    def __bool__(self) -> bool:
        return self.unlisted

    def __int__(self) -> int:
        return self.owner_id

    def __str__(self) -> str:
        return self.id

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Link) and self.__repr__() == repr(other)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        attrs: dict = {
            key: repr(getattr(self, key))
            for key in self.__slots__
            if key[0] != '_' and hasattr(self, key)
        }

        return '<Link %s>' % ', '.join([f'{k}={v}' for k, v in attrs.items()])


class Embed:
    """
    Represents a :class:`dsc.Link` embed.
    
    .. container:: operations

        .. describe:: x == y

             Checks if two embeds are equal.

        .. describe:: x != y

             Checks if two embeds are not equal.

        .. describe:: str(x)

             Returns the title of the embed.

    Attributes
    ----------
    title: :class:`str`
        The title of the embed
    description: :class:`str`
        The description of the embed
    image: :class:`str`
        The image URL of the embed
    color: :class:`dsc.Color`
        The color of the embed
    """

    __slots__ = ('title', 'description', 'color', 'image', 'saying')

    def __init__(self, **kwargs):
        self.image: str = kwargs.get('image', None)
        if type(c := kwargs.get('color', None)) is Union[str, int]:
            self.color: Color = Color(c)
        elif isinstance(c, Color):
            self.color: Color = c
        else:
            raise TypeError(f"Expected color to be 'int', 'str' or 'dsc.Colour' - got {c.__class__.__name__}")
        self.description: str = kwargs.get('description', None)
        self.title: str = kwargs.get('title', None)

    @classmethod
    def from_dict(cls, data: dict) -> Embed:
        """
        Returns a :class:`dsc.Embed` object initialized by values from the passed dictionary

        Parameters
        ----------
        data: :class:`dict`
            The dictionary to initialize from

        Returns
        -------
        :class:`dsc.Embed`
            The initialized Embed
        """

        self: cls = cls.__new__(cls)

        self.saying = data.get('saying', None)
        self.image = data.get('image', None)
        self.color = data.get('color', None)
        self.description = data.get('description', None)
        self.title = data.get('title', None)

        return self

    def to_dict(self) -> dict:
        """
        Get the :class:`dsc.Embed` in the form of a :class:`dict`

        Returns
        -------
        :class:`dict`
            The dictionary product of the conversion
        """

        result: dict = {
            key: getattr(self, key)
            for key in self.__slots__
            if key[0] != '_' and hasattr(self, key)
        }

        return result

    def __str__(self) -> str:
        return self.title

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Embed) and self.__repr__() == repr(other)

    def __ne__(self, other: Any) -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return 'Embed(title={title}, description={description}, image={image}, color={color})' \
            .format(title=repr(self.title),
                    description=repr(self.description),
                    image=repr(self.image),
                    color=repr(self.color))


class Colour:
    """
    Represents a colour. This class is similar
    to a (red, green, blue) :class:`tuple`.

    There is an alias for this called Color.

    .. container:: operations

        .. describe:: x == y

             Checks if two colours are equal.

        .. describe:: x != y

             Checks if two colours are not equal.

        .. describe:: hash(x)

             Return the colour's hash.

        .. describe:: str(x)

             Returns the hex format for the colour.

    Attributes
    ------------
    value: Union[:class:`str`, :class:`int`]
        The value of the color in hex - can be ex. 0xefefef or #efefef
    """

    __slots__ = ('value',)

    def __init__(self, value: Union[str, int]):
        if not isinstance(value, (int, str)):
            raise TypeError(f'Expected int or str parameter, received {value.__class__.__name__} instead.')
        if isinstance(value, str):
            value: int = int(value[1:], 16)

        self.value: int = value

    def _get_byte(self, byte):
        return (self.value >> (8 * byte)) & 0xff

    def __eq__(self, other) -> bool:
        return isinstance(other, Colour) and self.value == other.value

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __str__(self) -> str:
        return '#{:0>6x}'.format(self.value)

    def __repr__(self):
        return 'Colour(value=%s)' % self.value

    def __hash__(self):
        return hash(self.value)

    @property
    def r(self):
        """:class:`int`: Returns the red component of the colour."""
        return self._get_byte(2)

    @property
    def g(self):
        """:class:`int`: Returns the green component of the colour."""
        return self._get_byte(1)

    @property
    def b(self):
        """:class:`int`: Returns the blue component of the colour."""
        return self._get_byte(0)

    def to_rgb(self):
        """Tuple[:class:`int`, :class:`int`, :class:`int`]: Returns an (r, g, b) tuple representing the colour."""
        return self.r, self.g, self.b

    @classmethod
    def from_rgb(cls, r, g, b):
        """Constructs a :class:`dsc.Colour` from an RGB tuple."""
        return cls((r << 16) + (g << 8) + b)

    @classmethod
    def from_hsv(cls, h, s, v):
        """Constructs a :class:`dsc.Colour` from an HSV tuple."""
        rgb = hsv_to_rgb(h, s, v)
        return cls.from_rgb(*(int(x * 255) for x in rgb))

    @classmethod
    def default(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0``."""

        return cls(0)

    @classmethod
    def teal(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0x1abc9c``."""

        return cls(0x1abc9c)

    @classmethod
    def dark_teal(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0x11806a``."""

        return cls(0x11806a)

    @classmethod
    def green(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0x2ecc71``."""

        return cls(0x2ecc71)

    @classmethod
    def dark_green(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0x1f8b4c``."""

        return cls(0x1f8b4c)

    @classmethod
    def blue(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0x3498db``."""

        return cls(0x3498db)

    @classmethod
    def dark_blue(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0x206694``."""

        return cls(0x206694)

    @classmethod
    def purple(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0x9b59b6``."""

        return cls(0x9b59b6)

    @classmethod
    def dark_purple(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0x71368a``."""

        return cls(0x71368a)

    @classmethod
    def magenta(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0xe91e63``."""

        return cls(0xe91e63)

    @classmethod
    def dark_magenta(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0xad1457``."""

        return cls(0xad1457)

    @classmethod
    def gold(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0xf1c40f``."""

        return cls(0xf1c40f)

    @classmethod
    def dark_gold(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0xc27c0e``."""

        return cls(0xc27c0e)

    @classmethod
    def orange(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0xe67e22``."""

        return cls(0xe67e22)

    @classmethod
    def dark_orange(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0xa84300``."""

        return cls(0xa84300)

    @classmethod
    def red(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0xe74c3c``."""

        return cls(0xe74c3c)

    @classmethod
    def dark_red(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0x992d22``."""

        return cls(0x992d22)

    @classmethod
    def lighter_grey(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0x95a5a6``."""

        return cls(0x95a5a6)

    lighter_gray = lighter_grey

    @classmethod
    def dark_grey(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0x607d8b``."""

        return cls(0x607d8b)

    dark_gray = dark_grey

    @classmethod
    def light_grey(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0x979c9f``."""

        return cls(0x979c9f)

    light_gray = light_grey

    @classmethod
    def darker_grey(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0x546e7a``."""

        return cls(0x546e7a)

    darker_gray = darker_grey

    @classmethod
    def blurple(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0x7289da``."""

        return cls(0x7289da)

    @classmethod
    def greyple(cls):
        """A factory method that returns a :class:`dsc.Colour` with a value of ``0x99aab5``."""

        return cls(0x99aab5)

    @classmethod
    def dark_theme(cls):
        """
        A factory method that returns a :class:`dsc.Colour` with a value of ``0x36393F``.
        This will appear transparent on Discord's dark theme.
        """

        return cls(0x36393F)


Color = Colour

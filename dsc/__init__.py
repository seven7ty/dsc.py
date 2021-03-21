# -*- coding: utf-8 -*-

"""
dsc.gg API Wrapper
~~~~~~~~~~~~~~~~~~

A simple wrapper for the dsc.gg API.

:copyright: (c) 2020-2020 wulf
:license: MIT, see LICENSE for more details.
"""

from .client import Client
from .models import Embed, Colour, Color
from collections import namedtuple

__version__ = '1.1.3'
__title__ = 'dsc'
__license__ = 'MIT'
__author__ = 'wulf'
__email__ = 'wulf.developer@gmail.com'
__uri__ = "https://github.com/itsmewulf/dsc.py"
__copyright__ = 'Copyright 2020-2020 %s' % __author__


__path__ = __import__('pkgutil').extend_path(__path__, __name__)

VersionInfo = namedtuple('VersionInfo', 'major minor micro releaselevel serial')

version_info = VersionInfo(major=1, minor=0, micro=0, releaselevel='final', serial=0)

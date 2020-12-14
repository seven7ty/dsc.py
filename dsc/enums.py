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

from enum import Enum
from collections import namedtuple

__all__ = (
    'LinkType',
    'ResponseCodes'
)

DSCGGResponse = namedtuple('DSCGGResponse', ['code', 'meaning'])


class LinkType(Enum):
    """Used to correlate a link with its dsc.gg type"""

    Server = 'https://discord.gg/'
    Template = 'https://discord.com/template/'
    Bot = 'https://discord.com/oauth2/'


class ResponseCodes(Enum):
    payload_received: DSCGGResponse = DSCGGResponse(200, 'The content was successfully returned.')
    rate_limit: DSCGGResponse = DSCGGResponse(429, 'You have hit a rate limit')
    invalid_key: DSCGGResponse = DSCGGResponse(401, 'The API key you provided is invalid')
    not_found: DSCGGResponse = DSCGGResponse(404, 'The content was not found or returned blank')
    owner_blacklisted: DSCGGResponse = DSCGGResponse(403, 'The owner is blacklisted so nothing is returned')
    version_deprecated: DSCGGResponse = DSCGGResponse(410, 'The version of the API is no longer available')
    bad_request: DSCGGResponse = DSCGGResponse(400, 'Something in the request is not valid')
    link_taken: DSCGGResponse = DSCGGResponse(400, 'The link is not available, it is taken')
    link_created: DSCGGResponse = DSCGGResponse(201, 'Link was created successfully')
    link_updated: DSCGGResponse = DSCGGResponse(200, 'The link was updated successfully')
    link_deleted: DSCGGResponse = DSCGGResponse(200, 'The link was deleted successfully')
    owner_mismatch: DSCGGResponse = DSCGGResponse(403, 'You are not the owner so you can\'t do it')
    whitelist_only: DSCGGResponse = DSCGGResponse(403, 'The action is reserved for whitelisted apps only ')

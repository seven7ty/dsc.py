# -*- coding: utf-8 -*-

class NoToken(AttributeError):
    pass


class Unauthorized(ConnectionRefusedError):
    pass


class Forbidden(ConnectionRefusedError):
    pass


class BearerNoToken(AttributeError):
    pass


class BadLinkType(ValueError):
    pass


class InternalServerError(ConnectionError):
    pass


class BadRequest(ValueError):
    pass


class ServiceUnavailable(ConnectionError):
    pass

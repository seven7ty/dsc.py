from typing import Union


class Announcement:
    def __init__(self, data: dict):
        self.author: Union[str, None] = data.get("author", None)
        self.recipients: Union[str, None] = data.get("for", None)
        self.message: Union[str, None] = data.get("message", None)
        self.character: Union[str, None] = data.get("type", None)



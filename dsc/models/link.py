from typing import Union
from .embed import Embed
from ..utils import str_bool


class Link:
    def __init__(self, data: dict):
        if "s_name" not in data:
            self.embed: Union[Embed, None] = Embed(dict(data.get("embed"))) if "embed" in dict(data) else None
        else:
            self.agents: Union[str, None] = data.get("agents", None)
            self.click_other: Union[int, None] = data.get("click_other", None)
            self.embed: Embed = Embed(
                {"title": data.get("s_name", None), "desc": data.get("desc", None), "color": data.get('color'),
                 "saying": data.get("saying", None), "image": data.get('image', None)})
        self.type: Union[str, None] = data.get("type", None)
        self.suspended: bool = str_bool(data.get("suspended"))
        self.unique: Union[int, None] = int(data.get("unique", None))
        self.recent: tuple = (data.get("recent", None), int(data.get("recent_time")))
        self.redirect: Union[str, None] = data.get("redirect", None)
        self.owner_id: Union[int, None] = int(data.get("owner", None))
        self.clicks: Union[int, None] = int(data.get("clicks"))

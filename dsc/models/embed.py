from typing import Union


class Embed:
    def __init__(self, data: dict):
        self.title: Union[str, None] = data.get("title", None)
        self.description: Union[str, None] = data.get("desc", None)
        self.saying: Union[str, None] = data.get("saying", None)
        self.image: Union[str, None] = data.get("image", None)
        self.color: Union[str, None] = data.get("color", None)

    def __str__(self) -> str:
        return self.title

from .interface import AliasCacher


class MemoryAliasCacher(AliasCacher):
    _aliases: dict[int, str]

    def __init__(self):
        self._aliases = {}

    def check(self, user_id: int, alias: str | None) -> bool:
        return self.get(user_id) == alias

    def get(self, user_id: int) -> str | None:
        return self._aliases.get(user_id, None)

    def set(self, user_id: int, alias: str | None):
        self._aliases[user_id] = alias

    def delete(self, user_id: int):
        if user_id in self._aliases:
            del self._aliases[user_id]


__all__ = ["MemoryAliasCacher"]

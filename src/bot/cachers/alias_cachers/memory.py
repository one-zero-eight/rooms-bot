from .interface import AliasCacher, UserInfo


class MemoryAliasCacher(AliasCacher):
    _aliases: dict[int, UserInfo]

    def __init__(self):
        self._aliases = {}

    def check(self, user_id: int, info: UserInfo) -> bool:
        return self.get(user_id) == info

    def get(self, user_id: int) -> UserInfo:
        return self._aliases.get(user_id, None)

    def set(self, user_id: int, info: UserInfo):
        self._aliases[user_id] = info

    def delete(self, user_id: int):
        if user_id in self._aliases:
            del self._aliases[user_id]


__all__ = ["MemoryAliasCacher"]

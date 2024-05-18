import dataclasses
from abc import ABC, abstractmethod


@dataclasses.dataclass
class UserInfo:
    alias: str | None
    fullname: str


class AliasCacher(ABC):
    @abstractmethod
    def check(self, user_id: int, info: UserInfo) -> bool:
        pass

    @abstractmethod
    def get(self, user_id: int) -> UserInfo:
        pass

    @abstractmethod
    def set(self, user_id: int, info: UserInfo):
        pass

    @abstractmethod
    def delete(self, user_id: int):
        pass


__all__ = ["AliasCacher", "UserInfo"]

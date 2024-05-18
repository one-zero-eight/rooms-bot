from abc import ABC, abstractmethod


class AliasCacher(ABC):
    @abstractmethod
    def check(self, user_id: int, alias: str | None) -> bool:
        pass

    @abstractmethod
    def get(self, user_id: int) -> str | None:
        pass

    @abstractmethod
    def set(self, user_id: int, alias: str | None):
        pass

    @abstractmethod
    def delete(self, user_id: int):
        pass


__all__ = ["AliasCacher"]

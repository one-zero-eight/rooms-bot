import re
from dataclasses import dataclass
from typing import Callable


@dataclass
class RoomDialogStartData:
    id: int
    name: str


@dataclass
class ConfirmationDialogStartData:
    content: str
    yes_message: str | None = None
    no_message: str | None = "Canceled"
    format: str = "Are you sure {}?"
    yes_button: str = "Yes"
    no_button: str = "No"

    @property
    def question(self) -> str:
        return self.format.format(self.content)


@dataclass
class IncomingInvitationDialogStartData:
    can_accept: bool


@dataclass
class TaskViewDialogStartData:
    task_id: int


@dataclass
class PromptDialogStartData:
    content: str
    cancel_message: str | None = "Canceled"
    cancel_button: str = "Cancel"
    format: str = "Enter {}"
    filter: re.Pattern | Callable[[str], bool] | None = None

    @property
    def prompt(self) -> str:
        return self.format.format(self.content)

    def validate(self, text: str) -> bool:
        if self.filter is None:
            return True
        if isinstance(self.filter, re.Pattern):
            return self.filter.fullmatch(text) is not None
        if callable(self.filter):
            return self.filter(text)
        raise TypeError("Filter's type is incorrect")


__all__ = [
    "RoomDialogStartData",
    "ConfirmationDialogStartData",
    "IncomingInvitationDialogStartData",
    "TaskViewDialogStartData",
    "PromptDialogStartData",
]

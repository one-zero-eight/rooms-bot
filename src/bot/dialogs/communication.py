from dataclasses import dataclass


@dataclass
class CreateRoomDialogResult:
    name: str | None = None
    created: bool = True


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


__all__ = [
    "CreateRoomDialogResult",
    "RoomDialogStartData",
    "ConfirmationDialogStartData",
    "IncomingInvitationDialogStartData",
]

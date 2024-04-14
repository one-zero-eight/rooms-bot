from dataclasses import dataclass


@dataclass
class CreateRoomDialogResult:
    name: str | None
    created: bool = True


@dataclass
class RoomDialogStartData:
    id: int
    name: str


__all__ = ["CreateRoomDialogResult", "RoomDialogStartData"]

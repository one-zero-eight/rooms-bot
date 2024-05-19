from datetime import datetime

from pydantic import BaseModel


class TaskDailyInfo(BaseModel):
    id: int
    name: str
    today_user_id: int | None


class DailyInfoResponse(BaseModel):
    tasks: list[TaskDailyInfo]


class UserInfo(BaseModel):
    alias: str | None
    fullname: str | None

    def __init__(self, alias: str, fullname: str):
        super().__init__(alias=alias, fullname=fullname)

    def empty(self) -> bool:
        return self.alias is None and self.fullname is None

    @property
    def repr(self) -> str:
        return self.fullname + (f" (@{self.alias})" if self.alias is not None else "")


class IncomingInvitationInfo(BaseModel):
    id: int
    sender: UserInfo
    room: int
    room_name: str


class IncomingInvitationsResponse(BaseModel):
    invitations: list[IncomingInvitationInfo]


class RoomInfoResponse(BaseModel):
    id: int
    name: str
    users: list[UserInfo]


class Task(BaseModel):
    id: int
    name: str
    inactive: bool


class TaskListResponse(BaseModel):
    tasks: list[Task]


class TaskInfoResponse(BaseModel):
    name: str
    description: str | None
    start_date: datetime
    period: int
    order_id: int | None
    inactive: bool


class SentInvitationInfo(BaseModel):
    id: int
    addressee: str
    room: int
    room_name: str


class SentInvitationsResponse(BaseModel):
    invitations: list[SentInvitationInfo]


class OrderInfoResponse(BaseModel):
    users: list[int]

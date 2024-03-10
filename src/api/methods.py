import os

import requests

from src.api.schemas.method_input_schemas import (
    CreateTaskBody,
    ModifyTaskBody,
)
from src.api.schemas.method_output_schemas import (
    DailyInfoResponse,
    IncomingInvitationInfo,
    RoomInfoResponse,
    TaskInfoResponse,
    SentInvitationInfo,
    Task,
)


class InNoHassleMusicRoomAPI:
    url: str
    secret: str

    def _post(self, path: str, user_id: int = None, **data: any) -> any:
        if user_id is not None:
            data["user_id"] = user_id
        r = requests.post(self.url + path, json=data, headers={"X-Token": self.secret})
        if r.status_code != 200:
            if r.status_code in (400, 422):
                json = r.json()
                if r.status_code == 400 and "code" in json:
                    raise RuntimeError(f"{json['code']}. {json['detail']}")
                elif r.status_code == 422:
                    raise RuntimeError(json["detail"])
            raise RuntimeError(r.text)
        return r.json()

    def __init__(self, url: str, secret: str) -> None:
        self.url = url
        self.secret = secret

    def create_user(self, user_id: int) -> int:
        return self._post("/bot/user/create", user_id)

    def create_room(self, name: str, user_id: int) -> int:
        return self._post("/bot/room/create", user_id, room={"name": name})

    def invite_person(self, alias: str, user_id: int) -> int:
        return self._post("/bot/invitation/create", user_id, addressee={"alias": alias})

    def accept_invitation(self, id_: int, user_id: int) -> int:
        return self._post("/bot/invitation/accept", user_id, invitation={"id": id_})

    def create_order(self, users: list[int], user_id: int) -> int:
        return self._post("/bot/order/create", user_id, order={"users": users})

    def create_task(self, body: CreateTaskBody, user_id: int) -> int:
        return self._post("/bot/task/create", user_id, task=body.model_dump())

    def modify_task(self, body: ModifyTaskBody, user_id: int) -> bool:
        return self._post("/bot/task/modify", user_id, task=body.model_dump())

    def get_daily_info(self, user_id: int) -> DailyInfoResponse:
        return DailyInfoResponse.model_validate(
            self._post("/bot/room/daily_info", user_id)
        )

    def get_incoming_invitations(
        self, alias: str, user_id: int
    ) -> list[IncomingInvitationInfo]:
        return [
            IncomingInvitationInfo.model_validate(obj)
            for obj in self._post("/bot/invitation/inbox", user_id, alias=alias)[
                "invitations"
            ]
        ]

    def get_room_info(self, user_id: int) -> RoomInfoResponse:
        return RoomInfoResponse.model_validate(self._post("/bot/room/info", user_id))

    def leave_room(self, user_id: int) -> bool:
        return self._post("/bot/room/leave", user_id)

    def get_tasks(self, user_id: int) -> list[Task]:
        return [
            Task.model_validate(obj)
            for obj in self._post("/bot/task/list", user_id)["tasks"]
        ]

    def get_task_info(self, id_: int, user_id: int) -> TaskInfoResponse:
        return TaskInfoResponse.model_validate(
            self._post("/bot/task/info", user_id, task={"id": id_})
        )

    def get_sent_invitations(self, user_id: int) -> list[SentInvitationInfo]:
        return [
            SentInvitationInfo.model_validate(obj)
            for obj in self._post("/bot/invitation/sent", user_id)["invitations"]
        ]

    def delete_invitation(self, id_: int, user_id: int) -> bool:
        return self._post("/bot/invitation/delete", user_id, invitation={"id": id_})

    def reject_invitation(self, id_: int, user_id: int) -> bool:
        return self._post("/bot/invitation/reject", user_id, invitation={"id": id_})

    def get_order_info(self, id_: int, user_id: int) -> list[int]:
        return self._post("/bot/order/info", user_id, order={"id": id_})["users"]


api_client = InNoHassleMusicRoomAPI(os.getenv("API_URL"), os.getenv("API_SECRET"))


__all__ = ["InNoHassleMusicRoomAPI", "api_client"]

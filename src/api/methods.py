import aiohttp

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

    def __init__(self, url: str, secret: str) -> None:
        self.url = url
        self.secret = secret

    async def _post(self, path: str, user_id: int = None, **data: any) -> any:
        if user_id is not None:
            data["user_id"] = user_id
        async with aiohttp.ClientSession() as session:
            r: aiohttp.ClientResponse
            async with session.post(self.url + path, json=data, headers={"X-Token": self.secret}) as r:
                if r.status != 200:
                    if r.status in (400, 422):
                        json = await r.json()
                        if r.status == 400 and "code" in json:
                            raise RuntimeError(f"{json['code']}. {json['detail']}")
                        elif r.status == 422:
                            raise RuntimeError(json["detail"])
                    raise RuntimeError(await r.text())
                return await r.json()

    async def create_user(self, user_id: int) -> int:
        return await self._post("/bot/user/create", user_id)

    async def create_room(self, name: str, user_id: int) -> int:
        return await self._post("/bot/room/create", user_id, room={"name": name})

    async def invite_person(self, alias: str, user_id: int) -> int:
        return await self._post("/bot/invitation/create", user_id, addressee={"alias": alias})

    async def accept_invitation(self, id_: int, user_id: int) -> int:
        return await self._post("/bot/invitation/accept", user_id, invitation={"id": id_})

    async def create_order(self, users: list[int], user_id: int) -> int:
        return await self._post("/bot/order/create", user_id, order={"users": users})

    async def create_task(self, body: CreateTaskBody, user_id: int) -> int:
        return await self._post("/bot/task/create", user_id, task=body.model_dump())

    async def modify_task(self, body: ModifyTaskBody, user_id: int) -> bool:
        return await self._post("/bot/task/modify", user_id, task=body.model_dump())

    async def get_daily_info(self, user_id: int) -> DailyInfoResponse:
        return DailyInfoResponse.model_validate(await self._post("/bot/room/daily_info", user_id))

    async def get_incoming_invitations(self, alias: str, user_id: int) -> list[IncomingInvitationInfo]:
        return [
            IncomingInvitationInfo.model_validate(obj)
            for obj in await self._post("/bot/invitation/inbox", user_id, alias=alias)["invitations"]
        ]

    async def get_room_info(self, user_id: int) -> RoomInfoResponse:
        return RoomInfoResponse.model_validate(await self._post("/bot/room/info", user_id))

    async def leave_room(self, user_id: int) -> bool:
        return await self._post("/bot/room/leave", user_id)

    async def get_tasks(self, user_id: int) -> list[Task]:
        return [Task.model_validate(obj) for obj in await self._post("/bot/task/list", user_id)["tasks"]]

    async def get_task_info(self, id_: int, user_id: int) -> TaskInfoResponse:
        return TaskInfoResponse.model_validate(await self._post("/bot/task/info", user_id, task={"id": id_}))

    async def get_sent_invitations(self, user_id: int) -> list[SentInvitationInfo]:
        return [
            SentInvitationInfo.model_validate(obj)
            for obj in await self._post("/bot/invitation/sent", user_id)["invitations"]
        ]

    async def delete_invitation(self, id_: int, user_id: int) -> bool:
        return await self._post("/bot/invitation/delete", user_id, invitation={"id": id_})

    async def reject_invitation(self, id_: int, user_id: int) -> bool:
        return await self._post("/bot/invitation/reject", user_id, invitation={"id": id_})

    async def get_order_info(self, id_: int, user_id: int) -> list[int]:
        return await self._post("/bot/order/info", user_id, order={"id": id_})["users"]

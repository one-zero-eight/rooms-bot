from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Dialog, Window, ShowMode
from aiogram_dialog.widgets.kbd import Group, Select, Button, Row
from aiogram_dialog.widgets.text import Format, Const, List

from src.api import client
from src.bot.cachers import UserInfo
from src.bot.dialogs.dialog_communications import CreateOrderStartData
from src.bot.dialogs.states import CreateOrderSG


class CreateOrderConsts:
    ADD_FIRST_HEADER = "Constructing an order...\nAdd the first member"
    ADD_MULTIPLE_HEADER = "Constructing an order...\nMembers:"
    CANCEL_BUTTON_TEXT = "Cancel"
    FINISH_BUTTON_TEXT = "Finish"
    SKIP_BUTTON_TEXT = "Set no order"

    ROOMMATE_SELECT_ID = "roommate_select"
    CANCEL_BUTTON_ID = "cancel_button"
    FINISH_BUTTON_ID = "finish_button"
    SKIP_BUTTON_ID = "skip_button"


class Events:
    @staticmethod
    async def on_start(start_data: dict, manager: DialogManager):
        start_data: CreateOrderStartData = start_data["input"]
        manager.dialog_data["allow_none"] = start_data.allow_none
        room_info = await client.get_room_info(start_data.user_id)
        manager.dialog_data["roommates"] = {u.id: u for u in room_info.users}
        manager.dialog_data["order"] = []

    @staticmethod
    async def on_cancel(callback: CallbackQuery, widget, manager: DialogManager):
        await callback.bot.send_message(callback.message.chat.id, "Canceled")
        await manager.done((False, None), show_mode=ShowMode.NO_UPDATE)

    @staticmethod
    async def on_select_roommate(callback: CallbackQuery, widget, manager: DialogManager, roommate_id: int):
        manager.dialog_data["order"].append(roommate_id)
        if len(manager.dialog_data["order"]) == 1:
            await manager.switch_to(CreateOrderSG.multiple)
        else:
            await manager.show()

    @staticmethod
    async def on_select_none(callback: CallbackQuery, widget, manager: DialogManager):
        await callback.bot.send_message(callback.message.chat.id, "No order was selected")
        await manager.done((True, None), show_mode=ShowMode.NO_UPDATE)

    @staticmethod
    async def on_finish(callback: CallbackQuery, widget, manager: DialogManager):
        order_id = await client.create_order(manager.dialog_data["order"], manager.event.from_user.id)
        await manager.done((True, order_id), show_mode=ShowMode.NO_UPDATE)


roommate_select = Group(
    Select(
        Format("{item.fullname}"),
        items="roommates",
        item_id_getter=lambda r: r.id,
        on_click=Events.on_select_roommate,
        type_factory=int,
        id=CreateOrderConsts.ROOMMATE_SELECT_ID,
    ),
    width=2,
)

cancel_button = Button(
    Const(CreateOrderConsts.CANCEL_BUTTON_TEXT),
    id=CreateOrderConsts.CANCEL_BUTTON_ID,
    on_click=Events.on_cancel,
)

skip_button = Button(
    Const(CreateOrderConsts.SKIP_BUTTON_TEXT),
    id=CreateOrderConsts.SKIP_BUTTON_ID,
    on_click=Events.on_select_none,
)


async def getter(dialog_manager: DialogManager, **kwargs) -> dict:
    roommates: dict[int, UserInfo] = dialog_manager.dialog_data["roommates"]
    return {
        "roommates": roommates.values(),
        "order": [roommates[id_].fullname for id_ in dialog_manager.dialog_data["order"]],
    }


create_order_dialog = Dialog(
    Window(
        Const(CreateOrderConsts.ADD_FIRST_HEADER),
        roommate_select,
        Row(
            skip_button,
            cancel_button,
        ),
        state=CreateOrderSG.first,
    ),
    Window(
        Const(CreateOrderConsts.ADD_MULTIPLE_HEADER),
        List(
            Format("{pos}) {item}"),
            items="order",
        ),
        roommate_select,
        Row(
            skip_button,
            cancel_button,
        ),
        Button(
            Const(CreateOrderConsts.FINISH_BUTTON_TEXT),
            id=CreateOrderConsts.FINISH_BUTTON_ID,
            on_click=Events.on_finish,
        ),
        state=CreateOrderSG.multiple,
    ),
    getter=getter,
    on_start=Events.on_start,
)

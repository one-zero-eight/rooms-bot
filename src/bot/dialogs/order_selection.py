from dataclasses import dataclass
from typing import Sequence

from aiogram.types import CallbackQuery
from aiogram_dialog import Dialog, Window, DialogManager, ShowMode
from aiogram_dialog.widgets.kbd import Select, Start, Group, Button
from aiogram_dialog.widgets.text import Const, List, Format, Multi

from src.api import client
from src.api.schemas.method_output_schemas import ListOfOrdersResponse
from src.bot.dialogs.states import OrderSelectionSG


class SelectionWindowConsts:
    HEADER_TEXT = "Select an order of roommates:"
    CREATE_NEW_BUTTON = "Create new"
    SELECT_NONE_BUTTON = "Leave empty"
    CANCEL_BUTTON = "Cancel"

    SELECT_ID = "select"
    CREATE_NEW_BUTTON_ID = "create_new_button"
    SELECT_NONE_BUTTON_ID = "select_none_button"
    CANCEL_BUTTON_ID = "cancel_button"


@dataclass
class OrderRepresentation:
    id: int
    users: list[int]


class Loader:
    @staticmethod
    async def load_orders(manager: DialogManager):
        data: ListOfOrdersResponse = await client.list_of_orders(manager.event.from_user.id)
        manager.dialog_data["orders"] = [OrderRepresentation(k, v) for k, v in data.orders.items()]
        manager.dialog_data["users"] = data.users


class Events:
    @staticmethod
    async def on_start(start_data: dict, manager: DialogManager):
        await Loader.load_orders(manager)

    @staticmethod
    async def on_select_order(callback: CallbackQuery, widget, manager: DialogManager, order_id: str):
        await manager.done((True, int(order_id)))

    @staticmethod
    async def on_select_none(callback: CallbackQuery, widget, manager: DialogManager):
        await manager.done((True, None), show_mode=ShowMode.EDIT)

    @staticmethod
    async def on_cancel(callback: CallbackQuery, widget, manager: DialogManager):
        await manager.done((False, None), show_mode=ShowMode.EDIT)


async def getter(dialog_manager: DialogManager, **kwargs):
    return {
        "orders": dialog_manager.dialog_data["orders"],
        "users": dialog_manager.dialog_data["users"],
    }


def get_formated_order_members(data: dict) -> Sequence[str]:
    result: list[str] = []
    for i, user_id in enumerate(data["item"].users):
        fullname = data["data"]["users"][user_id].fullname
        if i != 0:
            m = " - " + fullname
        else:
            m = fullname
        result.append(m)
    return result


select_order_dialog = Dialog(
    Window(
        Const(SelectionWindowConsts.HEADER_TEXT),
        List(
            Multi(
                Format("{pos}) "),
                List(
                    Format("{item}"),
                    items=get_formated_order_members,
                ),
                sep="",
            ),
            items="orders",
        ),
        Group(
            Select(
                Format("{pos}"),
                items="orders",
                item_id_getter=lambda item: item.id,
                on_click=Events.on_select_order,
                id=SelectionWindowConsts.SELECT_ID,
            ),
            width=4,
        ),
        Start(
            Const(SelectionWindowConsts.CREATE_NEW_BUTTON),
            id=SelectionWindowConsts.CREATE_NEW_BUTTON_ID,
            state=...,
        ),
        Button(
            Const(SelectionWindowConsts.SELECT_NONE_BUTTON),
            id=SelectionWindowConsts.SELECT_NONE_BUTTON_ID,
            on_click=Events.on_select_none,
        ),
        Button(
            Const(SelectionWindowConsts.CANCEL_BUTTON),
            id=SelectionWindowConsts.CANCEL_BUTTON_ID,
            on_click=Events.on_cancel,
        ),
        state=OrderSelectionSG.select,
        getter=getter,
    ),
    on_start=Events.on_start,
)

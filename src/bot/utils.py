from datetime import datetime
from typing import Callable, Awaitable, Any, TypeVar

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, SubManager

T = TypeVar("T")


def list_group_finder(
    list_name: str, id_func: Callable[[str], Any] = int
) -> Callable[
    [Callable[[CallbackQuery, Any, DialogManager, T], Awaitable]],
    Callable[[CallbackQuery, Any, DialogManager], Awaitable],
]:
    """
    A decorator for ``aiogram_dialog.widgets.kbd.ListGroup`` that finds the selected item in a list by id.
     Items should have an ``id`` field.

    The finder raises RuntimeError if the id is not found in the list.
    :param list_name: The list's name in ``DialogManager``'s dialog data
    :param id_func: A function to convert `aiogram-dialog`'s item id (given as a string) into any type
    """

    def decorator(
        func: Callable[[CallbackQuery, Any, DialogManager, T], Awaitable],
    ) -> Callable[[CallbackQuery, Any, DialogManager], Awaitable]:
        async def wrapped(callback: CallbackQuery, widget: Any, manager: DialogManager):
            assert isinstance(manager, SubManager)

            id_ = id_func(manager.item_id)
            items: list[T] = manager.dialog_data[list_name]
            for i in items:
                if i.id == id_:
                    await func(callback, widget, manager, i)
                    return
            else:
                raise RuntimeError("Selected non-existent item")

        return wrapped

    return decorator


def select_finder(
    list_name: str, id_func: Callable[[str], Any] = int
) -> Callable[
    [Callable[[CallbackQuery, Any, DialogManager, T], Awaitable]],
    Callable[[CallbackQuery, Any, DialogManager, str], Awaitable],
]:
    """
    A decorator for ``aiogram_dialog.widgets.kbd.Select`` that finds the selected item in a list by id.
    Items should have an ``id`` field.

    The finder raises RuntimeError if the id is not found in the list.
    :param id_func: A function to convert `aiogram-dialog`'s item id (given as a string) into any type
    :param list_name: The list's name in ``DialogManager``'s dialog data
    """

    def decorator(
        func: Callable[[CallbackQuery, Any, DialogManager, T], Awaitable],
    ) -> Callable[[CallbackQuery, Any, DialogManager, str], Awaitable]:
        async def wrapped(callback: CallbackQuery, widget: Any, manager: DialogManager, item_id: str):
            id_ = id_func(item_id)
            items: list[T] = manager.dialog_data[list_name]
            for item in items:
                if item.id == id_:
                    await func(callback, widget, manager, item)
                    return
            else:
                raise RuntimeError("Selected non-existent item")

        return wrapped

    return decorator


def parse_datetime(text: str) -> datetime:
    return datetime.strptime(text, "%d.%m.%Y %H:%M")


def datetime_validator(text: str) -> bool:
    try:
        parse_datetime(text)
    except ValueError:
        return False
    else:
        return True

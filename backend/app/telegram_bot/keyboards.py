from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.telegram_bot.backend_client import Station


def stations_keyboard(stations: list[Station]) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(
                text=f"{station.name} · {station.line}",
                callback_data=f"station:{station.id}",
            )
        ]
        for station in stations
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)
